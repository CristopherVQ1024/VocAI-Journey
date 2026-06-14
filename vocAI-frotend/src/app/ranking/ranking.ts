import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { VocationalTestService, RankingResult, RankingItem } from '../service/vocational-test.service';

@Component({
  selector: 'app-ranking',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './ranking.html',
  styleUrls: ['./ranking.scss']
})
export class RankingComponent implements OnInit {
  sessionId: string = '';
  ranking: RankingResult | null = null;
  cargando: boolean = true;
  error: string = '';

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
        this.cargarRanking();
      } else {
        this.error = 'No se encontró la sesión';
        this.cargando = false;
      }
    });
  }

  cargarRanking(): void {
    this.cargando = true;
    this.error = '';
    this.cdr.detectChanges();

    this.testService.getRanking(this.sessionId).subscribe({
      next: (data) => {
        this.ranking = data;
        this.cargando = false;
        this.cdr.detectChanges();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      },
      error: (err) => {
        console.error('Error al cargar ranking:', err);
        this.error = 'No se pudo cargar el ranking';
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  verDetalle(item: RankingItem): void {
    this.router.navigate(['/carrera-detalle'], {
      queryParams: { carrera: item.career.nombre }
    });
  }

  volver(): void {
    window.history.back();
  }
}