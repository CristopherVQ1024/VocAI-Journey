from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.services.comparison_service import ComparisonSectionService

from app.core.database import get_db
from app.models.session import (
    VocationalSession,
    SessionSelectedCareer,
    SessionSectionAnswer,
)
from app.models.comparison import ComparisonSection, CareerCard
from app.models.career import Career
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SelectCareersInput,
    SectionAnswerInput,
    SectionAnswerResponse,
    
)
from app.schemas.comparison import ComparisonStepResponse, ComparisonSectionResponse, CareerCardResponse, ComparisonSectionAdminResponse, ComparisonSectionCreate, ComparisonSectionUpdate, CareerCardAdminResponse, CareerCardCreate, CareerCardUpdate

router = APIRouter()


@router.get(
    "/sections",
    response_model=list[ComparisonSectionAdminResponse]
)
async def get_sections(
    db: AsyncSession = Depends(get_db),
):
    """
    Lista todas las secciones de comparación.
    Ordenadas según el flujo del journey.
    """
    return await ComparisonSectionService.get_all(db)

@router.post("/session", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Inicia una nueva sesión del journey.
    Funciona sin login usando guest_token generado por el frontend.
    """
    session = VocationalSession(
        guest_token=data.guest_token,
        status="in_progress",
    )
    db.add(session)
    await db.flush()
    return session


@router.post("/session/{session_id}/careers", status_code=201)
async def select_careers(
    session_id: str,
    data: SelectCareersInput,
    db: AsyncSession = Depends(get_db),
):
    """
    El alumno elige las 3 carreras que quiere comparar.
    Máximo 3 — se valida aquí.
    """
    if len(data.career_ids) != 3:
        raise HTTPException(status_code=400, detail="Debes seleccionar exactamente 3 carreras")

    # Verificar que la sesión existe
    result = await db.execute(
        select(VocationalSession).where(VocationalSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")

    # Guardar las 3 carreras seleccionadas
    for orden, career_id in enumerate(data.career_ids, start=1):
        score = data.compatibility_scores.get(str(career_id), 0.0)
        selected = SessionSelectedCareer(
            session_id=session.id,
            career_id=career_id,
            compatibility_score=score,
            selected_order=orden,
        )
        db.add(selected)

    return {"message": "Carreras seleccionadas correctamente", "session_id": str(session.id)}


@router.get("/session/{session_id}/step/{step_order}", response_model=ComparisonStepResponse)
async def get_step(
    session_id: str,
    step_order: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Devuelve el contenido de un paso del journey.
    step_order va del 1 al 8 según las comparison_sections.
    Incluye las 3 cards (una por carrera seleccionada).
    """
    # Obtener la sección correspondiente al paso
    result = await db.execute(
        select(ComparisonSection)
        .where(ComparisonSection.orden == step_order, ComparisonSection.activo == True)
    )
    section = result.scalar_one_or_none()
    if not section:
        raise HTTPException(status_code=404, detail=f"Paso {step_order} no encontrado")

    # Obtener las carreras seleccionadas en esta sesión
    result = await db.execute(
        select(SessionSelectedCareer)
        .where(SessionSelectedCareer.session_id == session_id)
        .order_by(SessionSelectedCareer.selected_order)
    )
    selected = result.scalars().all()
    if not selected:
        raise HTTPException(status_code=400, detail="No hay carreras seleccionadas para esta sesión")

    career_ids = [s.career_id for s in selected]

    # Obtener las cards de esas carreras para esta sección
    result = await db.execute(
        select(CareerCard)
        .where(
            CareerCard.section_id == section.id,
            CareerCard.career_id.in_(career_ids),
            CareerCard.is_active == True,
        )
    )
    cards = result.scalars().all()

    # Total de secciones activas
    total_result = await db.execute(
        select(ComparisonSection).where(ComparisonSection.activo == True)
    )
    total_steps = len(total_result.scalars().all())

    return ComparisonStepResponse(
        section=ComparisonSectionResponse.model_validate(section),
        cards=[CareerCardResponse.model_validate(c) for c in cards],
        total_steps=total_steps,
        current_step=step_order,
    )


@router.post("/session/{session_id}/answer", response_model=SectionAnswerResponse, status_code=201)
async def submit_answer(
    session_id: str,
    data: SectionAnswerInput,
    db: AsyncSession = Depends(get_db),
):
    """
    Guarda la elección del alumno en un paso.
    'Esta conectó más conmigo' → suma 10 puntos a esa carrera.
    """
    # Verificar que no haya respondido ya esta sección
    result = await db.execute(
        select(SessionSectionAnswer).where(
            SessionSectionAnswer.session_id == session_id,
            SessionSectionAnswer.section_id == data.section_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Ya respondiste esta sección")

    answer = SessionSectionAnswer(
        session_id=session_id,
        section_id=data.section_id,
        selected_career_id=data.selected_career_id,
        score_awarded=10,
    )
    db.add(answer)
    await db.flush()
    return answer

@router.get(
    "/sections/{section_id}",
    response_model=ComparisonSectionAdminResponse
)
async def get_section(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene una sección específica.
    """
    section = await ComparisonSectionService.get_by_id(
        db,
        section_id
    )

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Sección no encontrada"
        )

    return section

@router.post(
    "/sections",
    response_model=ComparisonSectionAdminResponse,
    status_code=201
)
async def create_section(
    data: ComparisonSectionCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una sección del journey.
    """

    existing_slug = await ComparisonSectionService.get_by_slug(
        db,
        data.slug
    )

    if existing_slug:
        raise HTTPException(
            status_code=400,
            detail="El slug ya existe"
        )

    section = ComparisonSection(
        nombre=data.nombre,
        slug=data.slug,
        descripcion=data.descripcion,
        orden=data.orden,
        activo=data.activo,
    )

    db.add(section)

    await db.flush()

    return section


@router.put(
    "/sections/{section_id}",
    response_model=ComparisonSectionAdminResponse
)
async def update_section(
    section_id: UUID,
    data: ComparisonSectionUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Edita una sección del journey.
    """

    section = await ComparisonSectionService.get_by_id(
        db,
        section_id
    )

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Sección no encontrada"
        )

    update_data = data.model_dump(exclude_unset=True)

    # validar slug único
    if "slug" in update_data:
        existing_slug = await ComparisonSectionService.get_by_slug(
            db,
            update_data["slug"]
        )

        if existing_slug and existing_slug.id != section.id:
            raise HTTPException(
                status_code=400,
                detail="El slug ya existe"
            )

    for key, value in update_data.items():
        setattr(section, key, value)

    await db.flush()

    return section

@router.patch(
    "/sections/{section_id}/toggle",
    response_model=ComparisonSectionAdminResponse
)
async def toggle_section(
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Activa o desactiva una sección.
    """
    section = await ComparisonSectionService.get_by_id(
        db,
        section_id
    )

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Sección no encontrada"
        )

    section.activo = not section.activo

    await db.flush()

    return section


@router.get(
    "/cards",
    response_model=list[CareerCardAdminResponse]
)
async def get_cards(
    db: AsyncSession = Depends(get_db),
):
    """
    Lista todas las cards de carreras.
    Admin panel.
    """
    return await ComparisonSectionService.get_all_cards(db)

@router.get(
    "/cards/{card_id}",
    response_model=CareerCardAdminResponse
)
async def get_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Obtiene una card específica.
    """
    card = await ComparisonSectionService.get_card_by_id(
        db,
        card_id
    )

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Card no encontrada"
        )

    return card


@router.post(
    "/cards",
    response_model=CareerCardAdminResponse,
    status_code=201
)
async def create_card(
    data: CareerCardCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Crea una card markdown de carrera.
    """

    # validar carrera
    career_result = await db.execute(
        select(Career)
        .where(Career.id == data.career_id)
    )
    career = career_result.scalar_one_or_none()

    if not career:
        raise HTTPException(
            status_code=404,
            detail="Carrera no encontrada"
        )

    # validar sección
    section_result = await db.execute(
        select(ComparisonSection)
        .where(ComparisonSection.id == data.section_id)
    )
    section = section_result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=404,
            detail="Sección no encontrada"
        )

    # evitar duplicado
    existing = await ComparisonSectionService.get_card_by_career_and_section(
        db,
        data.career_id,
        data.section_id
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una card para esta carrera y sección"
        )

    card = CareerCard(
        career_id=data.career_id,
        section_id=data.section_id,
        markdown_content=data.markdown_content,
        orden=data.orden,
        is_active=data.is_active,
    )

    db.add(card)

    await db.flush()

    return card


@router.put(
    "/cards/{card_id}",
    response_model=CareerCardAdminResponse
)
async def update_card(
    card_id: UUID,
    data: CareerCardUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Edita una card markdown.
    """

    card = await ComparisonSectionService.get_card_by_id(
        db,
        card_id
    )

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Card no encontrada"
        )

    update_data = data.model_dump(exclude_unset=True)

    # validar duplicado career + section
    future_career_id = update_data.get(
        "career_id",
        card.career_id
    )

    future_section_id = update_data.get(
        "section_id",
        card.section_id
    )

    existing = await ComparisonSectionService.get_card_by_career_and_section(
        db,
        future_career_id,
        future_section_id
    )

    if existing and existing.id != card.id:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una card para esta carrera y sección"
        )

    for key, value in update_data.items():
        setattr(card, key, value)

    await db.flush()

    return card


@router.patch(
    "/cards/{card_id}/toggle",
    response_model=CareerCardAdminResponse
)
async def toggle_card(
    card_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Activa o desactiva una card.
    """

    card = await ComparisonSectionService.get_card_by_id(
        db,
        card_id
    )

    if not card:
        raise HTTPException(
            status_code=404,
            detail="Card no encontrada"
        )

    card.is_active = not card.is_active

    await db.flush()

    return card