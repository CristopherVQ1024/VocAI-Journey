import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CarreraDetalle } from './carrera-detalle';

describe('CarreraDetalle', () => {
  let component: CarreraDetalle;
  let fixture: ComponentFixture<CarreraDetalle>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CarreraDetalle],
    }).compileComponents();

    fixture = TestBed.createComponent(CarreraDetalle);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
