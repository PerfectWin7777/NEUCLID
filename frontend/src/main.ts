import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
// On importe AppComponent (le nouveau nom) et non plus App
// NOTE: Assure-toi que ton fichier s'appelle bien app.component.ts dans le dossier app/
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig)
    .catch((err) => console.error(err));