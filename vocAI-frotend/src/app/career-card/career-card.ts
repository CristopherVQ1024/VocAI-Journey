import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { VocationalTestService, ComparisonCard } from '../service/vocational-test.service';
import { MarkdownPipe } from '../ markdown.pipe';

@Component({
  selector: 'app-career-card',
  standalone: true,
  imports: [CommonModule, MarkdownPipe],
  templateUrl: './career-card.html',
  styleUrls: ['./career-card.scss']
})
export class CareerCardComponent implements OnInit {
  sessionId: string = '';
  currentStep: number = 1;
  totalSteps: number = 8;
  sectionTitle: string = '';
  sectionDesc: string = '';
  cards: ComparisonCard[] = [];
  selectedCardId: string | null = null;

  cargando: boolean = true;
  guardando: boolean = false;
  completado: boolean = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private testService: VocationalTestService,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.sessionId = params['session_id'] || '';

      if (this.sessionId) {
        this.cargarStep(1);
      } else {
        this.cargando = false;
      }
    });
  }

  cargarStep(step: number): void {
    this.cargando = true;
    this.selectedCardId = null;
    this.cdr.detectChanges();

    this.testService.getComparisonStep(this.sessionId, step).subscribe({
      next: (data) => {
        this.currentStep = data.current_step;
        this.totalSteps = data.total_steps;
        this.sectionTitle = data.section.nombre;
        this.sectionDesc = data.section.descripcion;
        this.cards = data.cards;
        this.cargando = false;
        this.cdr.detectChanges();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      },
      error: (err) => {
        console.error('Error al cargar step:', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  seleccionarCard(card: ComparisonCard): void {
    this.selectedCardId = card.career_id;
  }

  guardarYContinuar(): void {
    if (!this.selectedCardId || this.guardando) return;

    this.guardando = true;
    this.cdr.detectChanges();

    const cardSeleccionada = this.cards.find(c => c.career_id === this.selectedCardId);

    this.testService.saveAnswer(this.sessionId, {
      section_id: cardSeleccionada!.section_id,
      selected_career_id: this.selectedCardId
    }).subscribe({
      next: () => {
        this.guardando = false;

        if (this.currentStep < this.totalSteps) {
          this.cargarStep(this.currentStep + 1);
        } else {
          this.completado = true;
          this.cdr.detectChanges();
        }
      },
      error: (err) => {
        console.error('Error al guardar:', err);
        this.guardando = false;
        this.cdr.detectChanges();
      }
    });
  }

  verResultados(): void {
    this.router.navigate(['/comparison-results'], {
      queryParams: { session_id: this.sessionId }
    });
  }

  reiniciarComparacion(): void {
    this.completado = false;
    this.currentStep = 1;
    this.cargarStep(1);
  }

  volver(): void {
    window.history.back();
  }

  finalizarComparacion(): void {
    if (!this.selectedCardId || this.guardando) return;

    this.guardando = true;
    this.cdr.detectChanges();

    const cardSeleccionada = this.cards.find(c => c.career_id === this.selectedCardId);

    // Primero guardar la última respuesta
    this.testService.saveAnswer(this.sessionId, {
      section_id: cardSeleccionada!.section_id,
      selected_career_id: this.selectedCardId
    }).subscribe({
      next: () => {
        // Luego generar el ranking
        this.testService.generateRanking(this.sessionId).subscribe({
          next: () => {
            this.guardando = false;
            this.cdr.detectChanges();

            // Redirigir al componente de ranking
            this.router.navigate(['/ranking'], {
              queryParams: { session_id: this.sessionId }
            });
          },
          error: (err) => {
            console.error('Error al generar ranking:', err);
            this.guardando = false;
            this.cdr.detectChanges();
            alert('Error al generar el ranking');
          }
        });
      },
      error: (err) => {
        console.error('Error al guardar última respuesta:', err);
        this.guardando = false;
        this.cdr.detectChanges();
      }
    });
  }
}