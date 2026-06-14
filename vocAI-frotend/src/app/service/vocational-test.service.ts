import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

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

@Injectable({
  providedIn: 'root'
})
export class VocationalTestService {
  // Coloca aquí tu webhook de n8n
  private webhookUrl = 'http://localhost:5678/webhook-test/test-vocacional';

  constructor(private http: HttpClient) { }

  sendResults(data: TestResult): Observable<TestResponse> {    
    return this.http.post<TestResponse>(this.webhookUrl, data);
  }
}