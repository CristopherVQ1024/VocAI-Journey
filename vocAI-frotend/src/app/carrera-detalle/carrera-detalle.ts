import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { VocationalTestService, CarreraDetalle } from '../service/vocational-test.service';

@Component({
  selector: 'app-carrera-detalle',
  imports: [CommonModule],
  templateUrl: './carrera-detalle.html',
  styleUrls: ['./carrera-detalle.scss']
})
export class CarreraDetalleComponent implements OnInit {
  carreraNombre: string = '';
  carreraDetalle: CarreraDetalle | null = null;
  cargando: boolean = true;
  error: string = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private testService: VocationalTestService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      this.carreraNombre = params['carrera'] || '';

      if (this.carreraNombre) {
        this.cargarCarrera();
      } else {
        this.error = 'No se especificó una carrera';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  cargarCarrera(): void {
    this.cargando = true;
    this.error = '';
    this.cdr.detectChanges();

    this.testService.getCarreraDetalle(this.carreraNombre).subscribe({
      next: (data: any) => {
        const carrera = Array.isArray(data) ? data[0] : data;
        
        if (carrera) {
          this.carreraDetalle = carrera;
        } else {
          this.error = 'No se encontró información de esta carrera';
        }
        
        this.cargando = false;
        this.cdr.detectChanges();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      },
      error: (err) => {
        console.error('Error al cargar la carrera:', err);
        this.error = 'No se pudo cargar la información. Intenta nuevamente.';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  volver(): void {
    window.history.back();
  }
}