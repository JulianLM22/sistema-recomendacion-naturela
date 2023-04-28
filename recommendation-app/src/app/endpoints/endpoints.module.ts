import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ResultsComponent } from './results/results.component';
import { SearchComponent } from './search/search.component';

@NgModule({
  declarations: [
    ResultsComponent,
    SearchComponent,

  ],
  imports: [
    CommonModule,
    FormsModule
  ],
  exports: [
    ResultsComponent,
    SearchComponent
  ]
})

export class EndpointsModule { }
