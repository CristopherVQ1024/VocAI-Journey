import { Routes } from '@angular/router';
import { VocationalTest } from './vocational-test/vocational-test';
import { CarreraDetalleComponent } from './carrera-detalle/carrera-detalle';
import { LoginComponent } from './login/login';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'test-vocacional', component: VocationalTest },
  { path: 'carrera-detalle', component: CarreraDetalleComponent },
  { path: '**', redirectTo: '/login' }
];