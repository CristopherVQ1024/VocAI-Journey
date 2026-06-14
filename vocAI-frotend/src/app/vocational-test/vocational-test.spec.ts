import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VocationalTest } from './vocational-test';

describe('VocationalTest', () => {
  let component: VocationalTest;
  let fixture: ComponentFixture<VocationalTest>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VocationalTest],
    }).compileComponents();

    fixture = TestBed.createComponent(VocationalTest);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
