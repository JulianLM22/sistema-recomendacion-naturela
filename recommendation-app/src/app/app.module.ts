import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';
import { NgxUiLoaderModule } from "ngx-ui-loader";
import { SharedModule } from './shared/shared.module';
import { EndpointsModule } from './endpoints/endpoints.module';


@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    NgxUiLoaderModule,
    SharedModule,
    EndpointsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
