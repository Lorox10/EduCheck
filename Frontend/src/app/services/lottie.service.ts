import { Injectable } from '@angular/core';
import lottie, { AnimationItem } from 'lottie-web';

@Injectable({
  providedIn: 'root'
})
export class LottieService {
  private animations: { [key: string]: AnimationItem } = {};

  loadAnimation(
    container: HTMLElement | string,
    path: string,
    autoplay: boolean = true,
    loop: boolean = true,
    animationId?: string
  ): AnimationItem {
    const id = animationId || path;
    
    const animation = lottie.loadAnimation({
      container: typeof container === 'string' ? document.getElementById(container)! : container,
      renderer: 'svg',
      loop: loop,
      autoplay: autoplay,
      path: path
    });

    if (animationId) {
      this.animations[animationId] = animation;
    }

    return animation;
  }

  playAnimation(animationId: string): void {
    if (this.animations[animationId]) {
      this.animations[animationId].play();
    }
  }

  pauseAnimation(animationId: string): void {
    if (this.animations[animationId]) {
      this.animations[animationId].pause();
    }
  }

  stopAnimation(animationId: string): void {
    if (this.animations[animationId]) {
      this.animations[animationId].stop();
    }
  }

  destroyAnimation(animationId: string): void {
    if (this.animations[animationId]) {
      this.animations[animationId].destroy();
      delete this.animations[animationId];
    }
  }
}
