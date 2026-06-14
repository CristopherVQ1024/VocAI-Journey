import { CommonModule } from '@angular/common';
import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ChatbotWidget } from './chatbot-widget/chatbot-widget';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, CommonModule, ChatbotWidget],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('vocai-journey');
}