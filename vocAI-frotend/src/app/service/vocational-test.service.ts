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

@Injectable({
  providedIn: 'root'
})
export class VocationalTestService {

  // Webhook de n8n (no tocar)
  private webhookUrl = 'http://localhost:5678/webhook/test-vocacional';

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
}