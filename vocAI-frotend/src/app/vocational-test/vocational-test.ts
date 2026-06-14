import { Component, OnInit, Output, EventEmitter, NgZone, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { VocationalTestService, TestResult, TestResponse, CarreraRecomendada } from '../service/vocational-test.service';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';

@Component({
  selector: 'app-vocational-test',
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './vocational-test.html',
  styleUrls: ['./vocational-test.scss']
})
export class VocationalTest implements OnInit {
  @Output() carreraSeleccionada = new EventEmitter<CarreraRecomendada>();

  testForm!: FormGroup;
  isSubmitting = false;
  testResult: TestResponse | null = null;
  private readonly STORAGE_KEY = 'vocational-test-result';

  escalaInterpretacion: { [key: number]: string } = {
    1: 'Totalmente en desacuerdo',
    2: 'En desacuerdo',
    3: 'Neutral',
    4: 'De acuerdo',
    5: 'Totalmente de acuerdo'
  };

  questions: string[] = [
    'Me gusta resolver problemas matemáticos complejos.',
    'Disfruto leer sobre temas científicos y tecnológicos.',
    'Me interesa entender cómo funcionan las cosas a nivel mecánico.',
    'Prefiero actividades al aire libre que estar en una oficina.',
    'Me gusta dibujar, pintar o crear cosas visuales.',
    'Disfruto escribir historias, poemas o artículos.',
    'Me interesa la política y los temas sociales.',
    'Prefiero trabajar en equipo que de forma individual.',
    'Me gusta liderar grupos y tomar decisiones.',
    'Disfruto enseñar o explicar temas a otras personas.',
    'Me preocupa el medio ambiente y la ecología.',
    'Me interesa la economía y las finanzas.',
    'Disfruto cocinar y experimentar con recetas nuevas.',
    'Me gusta la música, ya sea escucharla o crearla.',
    'Prefiero trabajos que impliquen movimiento físico.',
    'Me interesa la anatomía y el funcionamiento del cuerpo humano.',
    'Disfruto los videojuegos y la tecnología interactiva.',
    'Me gusta organizar eventos y planificar actividades.',
    'Prefiero la estabilidad laboral aunque el trabajo no me apasione.',
    'Me interesa viajar y conocer otras culturas.',
    'Disfruto debatir y argumentar mis puntos de vista.',
    'Me gusta reparar objetos o aparatos descompuestos.',
    'Prefiero trabajos con horarios flexibles.',
    'Me interesa la programación y el desarrollo de software.',
    'Disfruto cuidar animales o plantas.',
    'Me gusta la fotografía y el diseño visual.',
    'Prefiero trabajar con datos y estadísticas.',
    'Me interesa la psicología y el comportamiento humano.',
    'Disfruto los deportes y la actividad física intensa.',
    'Me gusta el cine y la producción audiovisual.',
    'Prefiero emprendimientos propios a empleos fijos.',
    'Me interesa la filosofía y las preguntas existenciales.',
    'Disfruto construir o armar cosas con mis manos.',
    'Me gusta ayudar a personas en situaciones vulnerables.',
    'Prefiero trabajos rutinarios y predecibles.',
    'Me interesa la astronomía y el espacio exterior.',
    'Disfruto los idiomas y aprender lenguas extranjeras.',
    'Me gusta invertir y manejar recursos financieros.',
    'Prefiero trabajos creativos a trabajos estructurados.',
    'Me interesa la nutrición y la alimentación saludable.',
    'Disfruto los juegos de estrategia y lógica.',
    'Me gusta la moda y el diseño de vestuario.',
    'Prefiero tener varios proyectos simultáneos.',
    'Me interesa la robótica y la inteligencia artificial.',
    'Disfruto las actividades al aire libre como senderismo o camping.',
    'Me gusta investigar y profundizar en temas específicos.',
    'Prefiero trabajos con interacción social constante.',
    'Me interesa la arquitectura y el diseño de espacios.',
    'Disfruto navegar por internet y descubrir contenido nuevo.',
    'Me gusta participar en voluntariados y causas sociales.'
  ];

  options = [
    { value: 1, label: 'Totalmente en desacuerdo', shortLabel: 'Totalmente en desacuerdo' },
    { value: 2, label: 'En desacuerdo', shortLabel: 'En desacuerdo' },
    { value: 3, label: 'Neutral', shortLabel: 'Neutral' },
    { value: 4, label: 'De acuerdo', shortLabel: 'De acuerdo' },
    { value: 5, label: 'Totalmente de acuerdo', shortLabel: 'Totalmente de acuerdo' }
  ];

  constructor(
    private fb: FormBuilder,
    private testService: VocationalTestService,
    private router: Router,
    private cdr: ChangeDetectorRef
  ) { }

  ngOnInit(): void {
    this.buildForm();
    this.loadSavedResult();
  }

  private loadSavedResult(): void {
    const saved = localStorage.getItem(this.STORAGE_KEY);
    if (saved) {
      try {
        this.testResult = JSON.parse(saved);
      } catch (e) {
        console.error('Error al leer resultado guardado:', e);
        localStorage.removeItem(this.STORAGE_KEY);
      }
    }
  }

  buildForm(): void {
    const controls: any = {};
    this.questions.forEach((_, index) => {
      controls['q' + index] = [null, Validators.required];
    });
    this.testForm = this.fb.group(controls);
  }

  onSubmit(): void {
    if (this.testForm.invalid) {
      Object.keys(this.testForm.controls).forEach(key => {
        this.testForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.isSubmitting = true;

    const respuestas = this.questions.map((pregunta, index) => {
      const valor = this.testForm.get('q' + index)?.value;
      return {
        pregunta: pregunta,
        valor: valor,
        interpretacion: this.escalaInterpretacion[valor]
      };
    });

    const payload: TestResult = {
      escala: {
        1: 'Totalmente en desacuerdo',
        2: 'En desacuerdo',
        3: 'Neutral',
        4: 'De acuerdo',
        5: 'Totalmente de acuerdo'
      },
      respuestas: respuestas,
      total_preguntas: this.questions.length,
      fecha: new Date().toISOString()
    };

    this.testService.sendResults(payload).subscribe({
      next: (response: any) => {
        if (response.carreras_adicionales) {
          response.carreras_recomendadas = [
            ...response.carreras_recomendadas,
            ...response.carreras_adicionales
          ];
          delete response.carreras_adicionales;
        }

        const result: TestResponse = {
          perfil_general: response.perfil_general,
          carreras_recomendadas: response.carreras_recomendadas?.slice(0, 3),
          recomendacion_final: response.recomendacion_final
        };

        this.testResult = result;
        this.isSubmitting = false;

        localStorage.setItem(this.STORAGE_KEY, JSON.stringify(result));

        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.cdr.detectChanges();
      },
      error: (err: any) => {
        console.error('Error al enviar:', err);
        this.isSubmitting = false;
        this.cdr.detectChanges();
      }
    });
  }

  onCarreraClick(carrera: CarreraRecomendada): void {
    this.router.navigate(['/carrera-detalle'], {
      queryParams: { carrera: carrera.nombre }
    });
  }

  resetTest(): void {
    this.testResult = null;
    this.testForm.reset();

    localStorage.removeItem(this.STORAGE_KEY);

    window.scrollTo({ top: 0, behavior: 'smooth' });
    this.cdr.detectChanges();
  }
}