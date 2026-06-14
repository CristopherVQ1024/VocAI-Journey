import { Component, ElementRef, ViewChild, AfterViewChecked, ChangeDetectorRef, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { VocationalTestService } from '../service/vocational-test.service';

interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
}

@Component({
  selector: 'app-chatbot-widget',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chatbot-widget.html',
  styleUrl: './chatbot-widget.scss'
})
export class ChatbotWidget implements OnInit, AfterViewChecked {
  isOpen = false;
  isLoading = false;
  userInput = '';
  hideWidget = false;

  messages: ChatMessage[] = [
    { role: 'assistant', text: '¡Hola! Soy tu asistente vocacional. ¿Qué quieres saber sobre alguna carrera?' }
  ];

  @ViewChild('messagesContainer') messagesContainer!: ElementRef<HTMLDivElement>;

  constructor(
    private testService: VocationalTestService,
    private cdr: ChangeDetectorRef,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.checkRoute(this.router.url);

    this.router.events
      .pipe(filter((event) => event instanceof NavigationEnd))
      .subscribe((event) => {
        this.checkRoute((event as NavigationEnd).urlAfterRedirects);
      });
  }

  private checkRoute(url: string): void {
    this.hideWidget = url.startsWith('/login');
    this.cdr.detectChanges();
  }

  toggleChat(): void {
    this.isOpen = !this.isOpen;
  }

  sendMessage(): void {
    const text = this.userInput.trim();
    if (!text || this.isLoading) return;

    this.messages.push({ role: 'user', text });
    this.userInput = '';
    this.isLoading = true;

    this.testService.sendChatMessage(text).subscribe({
      next: (res) => {
        this.messages.push({ role: 'assistant', text: res.reply });
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          text: 'Ocurrió un error al conectar con el asistente. Intenta nuevamente.'
        });
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  ngAfterViewChecked(): void {
    if (this.messagesContainer) {
      const el = this.messagesContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }
}