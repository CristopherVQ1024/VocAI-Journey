import { Routes } from '@angular/router';
import { VocationalTest } from './vocational-test/vocational-test';
import { CarreraDetalleComponent } from './carrera-detalle/carrera-detalle';
import { LoginComponent } from './login/login';
import { CareerCardComponent } from './career-card/career-card';
import { RankingComponent } from './ranking/ranking';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'test-vocacional', component: VocationalTest },
  { path: 'carrera-detalle', component: CarreraDetalleComponent },
  { path: 'career-card', component: CareerCardComponent },
  { path: 'ranking', component: RankingComponent },
  { path: '**', redirectTo: '/login' }
];