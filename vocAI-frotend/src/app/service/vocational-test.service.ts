import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface QuestionResponse {
  pregunta: string;
  valor: number;
  interpretacion: string;
}

export interface TestResult {
  escala: {
    1: string;
    2: string;
    3: string;
    4: string;
    5: string;
  };
  respuestas: QuestionResponse[];
  total_preguntas: number;
  fecha: string;
}

export interface CarreraRecomendada {
  nombre: string;
  afinidad: number;
  categoria: string;
  motivo: string;
}

export interface PerfilGeneral {
  descripcion: string;
  fortalezas: string[];
  areas_predominantes: string[];
}

export interface TestResponse {
  perfil_general: PerfilGeneral;
  carreras_recomendadas: CarreraRecomendada[];
  recomendacion_final: string;
}

export interface CarreraDetalle {
  id: string;
  nombre: string;
  slug: string;
  descripcion_corta: string;
  modalidad: string;
  demanda_laboral: string;
  trabajo_remoto: boolean;
  salario_promedio: number;
  imagen_url: string | null;
  color_hex: string;
  faculty: {
    id: string;
    nombre: string;
    descripcion: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegistroRequest {
  nombres: string;
  apellidos: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  usuario: {
    id: string;
    nombres: string;
    apellidos: string;
    email: string;
  };
}

// Agrega estas interfaces
export interface ComparisonSession {
  id: string;
  user_id: string | null;
  guest_token: string | null;
  status: string;
  started_at: string;
  completed_at: string | null;
}

export interface CreateSessionRequest {
  nombre: string;
}

export interface AddCareersRequest {
  career_ids: string[];
  compatibility_scores: {
    [key: string]: number;
  };
}

export interface AddCareersResponse {
  message: string;
  session_id: string;
}

// Agrega estas interfaces
export interface ComparisonStep {
  section: {
    id: string;
    nombre: string;
    slug: string;
    descripcion: string;
    orden: number;
  };
  cards: ComparisonCard[];
  total_steps: number;
  current_step: number;
}

export interface ComparisonCard {
  id: string;
  career_id: string;
  section_id: string;
  markdown_content: string;
  orden: number;
}

export interface SaveAnswerRequest {
  section_id: string;
  selected_career_id: string;
}

export interface SaveAnswerResponse {
  message: string;
  session_id: string;
}

export interface RankingResult {
  session_id: string;
  results: RankingItem[];
}

export interface RankingItem {
  ranking_position: number;
  career: CarreraDetalle;
  compatibility_score: number;
  interaction_score: number;
  final_score: number;
  ai_justification: string | null;
}

export interface ChatbotResponse {
  reply: string;
}

@Injectable({
  providedIn: 'root'
})
export class VocationalTestService {

  // Webhook de n8n (no tocar)
  private webhookUrl = 'http://localhost:5678/webhook/test-vocacional';

  private chatbotWebhookUrl = 'http://localhost:5678/webhook/chatbot-vocacional'; 

  // Backend principal
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  // Test vocacional - Webhook n8n
  sendResults(data: TestResult): Observable<TestResponse> {
    return this.http.post<TestResponse>(this.webhookUrl, data);
  }

  // Detalle de carrera
  getCarreraDetalle(nombreCarrera: string): Observable<CarreraDetalle> {
    return this.http.get<CarreraDetalle>(`${this.apiUrl}/api/careers/?buscar=${encodeURIComponent(nombreCarrera)}`);
  }

  // Login
  login(data: LoginRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/login`, data);
  }

  // Registro
  registro(data: RegistroRequest): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/register`, data);
  }

  // Crear sesión de comparación
  crearSesionComparacion(data: CreateSessionRequest): Observable<ComparisonSession> {
    return this.http.post<ComparisonSession>(`${this.apiUrl}/api/comparison/session`, data);
  }

  // Agregar carreras a la sesión
  agregarCarrerasASesion(sessionId: string, data: AddCareersRequest): Observable<AddCareersResponse> {
    return this.http.post<AddCareersResponse>(`${this.apiUrl}/api/comparison/session/${sessionId}/careers`, data);
  }

  // Obtener step de comparación
  getComparisonStep(sessionId: string, step: number): Observable<ComparisonStep> {
    return this.http.get<ComparisonStep>(`${this.apiUrl}/api/comparison/session/${sessionId}/step/${step}`);
  }

  // Guardar respuesta
  saveAnswer(sessionId: string, data: SaveAnswerRequest): Observable<SaveAnswerResponse> {
    return this.http.post<SaveAnswerResponse>(`${this.apiUrl}/api/comparison/session/${sessionId}/answer`, data);
  }

  // Generar ranking
  generateRanking(sessionId: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/ranking/generate/${sessionId}`, {});
  }

  // Obtener ranking
  getRanking(sessionId: string): Observable<RankingResult> {
    return this.http.get<RankingResult>(`${this.apiUrl}/api/ranking/${sessionId}`);
  }

  sendChatMessage(message: string): Observable<ChatbotResponse> {
    return this.http.post<ChatbotResponse>(this.chatbotWebhookUrl, { message });
  }
}