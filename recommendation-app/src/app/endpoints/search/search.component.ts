import { Component, ElementRef, ViewChild} from '@angular/core';
import { EndpointsService } from '../services/endpoints.service';

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent{
  @ViewChild('Buscar') Buscar!: ElementRef<HTMLInputElement>;
  @ViewChild('BuscarCan') BuscarCan!: ElementRef<HTMLInputElement>;


  constructor(private endpointService: EndpointsService) {
  }

  buscar(): void {
    const valor = this.Buscar.nativeElement.value;
    const valor2 = this.BuscarCan.nativeElement.value;

    if (valor !== '' && valor2 !== '') {
      this.endpointService.buscarData(valor);
      this.endpointService.buscarPorId(valor, valor2);
      // this.endpointService.buscarCollab(valor, valor2);
      this.BuscarCan.nativeElement.value = '';
      this.Buscar.nativeElement.value = '';
    }
  }
}


