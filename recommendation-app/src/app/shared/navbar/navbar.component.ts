import { Component } from '@angular/core';
import { EndpointsService } from '../../endpoints/services/endpoints.service';
import { NgxUiLoaderService } from 'ngx-ui-loader';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent {


  constructor(private endpointsService: EndpointsService, private loader: NgxUiLoaderService) { }

  train() {
    this.endpointsService.entrenar();
    this.loader.start();
    setInterval(() => {
      this.loader.stop();
    }, 1500);
  }


}
