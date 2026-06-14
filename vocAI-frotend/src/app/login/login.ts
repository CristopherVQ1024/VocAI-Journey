import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { VocationalTestService } from '../service/vocational-test.service';

@Component({
  selector: 'app-login',  
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrls: ['./login.scss']
})
export class LoginComponent implements OnInit {
  isRegistro = false;
  cargando = false;
  mensajeError = '';
  mensajeExito = '';

  loginForm!: FormGroup;
  registroForm!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private router: Router,
    private authService: VocationalTestService
  ) { }

  ngOnInit(): void {
    this.buildForms();
  }

  buildForms(): void {
    // Formulario de Login
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]]
    });

    // Formulario de Registro
    this.registroForm = this.fb.group({
      nombres: ['', [Validators.required, Validators.minLength(2)]],
      apellidos: ['', [Validators.required, Validators.minLength(2)]],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  toggleModo(): void {
    this.isRegistro = !this.isRegistro;
    this.mensajeError = '';
    this.mensajeExito = '';
  }

  onLogin(): void {
    if (this.loginForm.invalid) {
      Object.keys(this.loginForm.controls).forEach(key => {
        this.loginForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.cargando = true;
    this.mensajeError = '';

    const loginData = this.loginForm.value;

    this.authService.login(loginData).subscribe({
      next: (response) => {
        console.log('Login exitoso:', response);
        // Guardar token en localStorage
        localStorage.setItem('token', response.token);
        localStorage.setItem('usuario', JSON.stringify(response.usuario));

        this.cargando = false;
        this.mensajeExito = 'Inicio de sesión exitoso';

        // Redirigir al test vocacional
        setTimeout(() => {
          this.router.navigate(['/test-vocacional']);
        }, 1000);
      },
      error: (err) => {
        console.error('Error en login:', err);
        this.mensajeError = 'Correo o contraseña incorrectos';
        this.cargando = false;

        // Simulación para desarrollo (quitar cuando haya backend)
        this.simularLogin();
      }
    });
  }

  onRegistro(): void {
    if (this.registroForm.invalid) {
      Object.keys(this.registroForm.controls).forEach(key => {
        this.registroForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.cargando = true;
    this.mensajeError = '';

    const registroData = this.registroForm.value;

    this.authService.registro(registroData).subscribe({
      next: (response) => {
        console.log('Registro exitoso:', response);
        localStorage.setItem('token', response.token);
        localStorage.setItem('usuario', JSON.stringify(response.usuario));

        this.cargando = false;
        this.mensajeExito = 'Registro exitoso. Bienvenido!';

        setTimeout(() => {
          this.router.navigate(['/test-vocacional']);
        }, 1000);
      },
      error: (err) => {
        console.error('Error en registro:', err);
        this.mensajeError = 'Error al registrar. Intenta nuevamente.';
        this.cargando = false;

        // Simulación para desarrollo (quitar cuando haya backend)
        this.simularRegistro();
      }
    });
  }

  // Simulación para desarrollo (quitar cuando haya backend)
  simularLogin(): void {
    setTimeout(() => {
      const mockResponse = {
        token: 'mock-token-123',
        usuario: {
          id: '1',
          nombres: 'Usuario',
          apellidos: 'Test',
          email: this.loginForm.value.email
        }
      };
      localStorage.setItem('token', mockResponse.token);
      localStorage.setItem('usuario', JSON.stringify(mockResponse.usuario));

      this.mensajeError = '';
      this.mensajeExito = 'Inicio de sesión exitoso (modo prueba)';
      this.cargando = false;

      setTimeout(() => {
        this.router.navigate(['/test-vocacional']);
      }, 1000);
    }, 1500);
  }

  simularRegistro(): void {
    setTimeout(() => {
      const mockResponse = {
        token: 'mock-token-456',
        usuario: {
          id: '2',
          nombres: this.registroForm.value.nombres,
          apellidos: this.registroForm.value.apellidos,
          email: this.registroForm.value.email
        }
      };
      localStorage.setItem('token', mockResponse.token);
      localStorage.setItem('usuario', JSON.stringify(mockResponse.usuario));

      this.mensajeError = '';
      this.mensajeExito = 'Registro exitoso (modo prueba)';
      this.cargando = false;

      setTimeout(() => {
        this.router.navigate(['/test-vocacional']);
      }, 1000);
    }, 1500);
  }
}