import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { Data, General, Prediction } from '../interface/predictions.interface';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})

@Component({
  selector: 'app-search',
  templateUrl: './search.component.html',
  styleUrls: ['./search.component.css']
})
export class SearchComponent implements OnInit{
  @ViewChild('Buscar') Buscar!: ElementRef<HTMLInputElement>;
  @ViewChild('BuscarCan') BuscarCan!: ElementRef<HTMLInputElement>;
  public resultados: Prediction[] = [];
  public data: Data[] = [];
  public errorMsg: string = '';

  constructor(private http: HttpClient) {
  }


  ngOnInit(): void {
    const storedMsg = localStorage.getItem('errorMsg');
    if (storedMsg) {
      this.errorMsg = storedMsg;
      localStorage.removeItem('errorMsg');
    }
  }

  onReload() {
    setTimeout(() => {
      window.location.reload();
    }, 300);
  }

  public text = '';
  public text2 = '';

  buscarPorId = (query: string) => {
    query = query.trim();

    const servicioUrl: string = 'http://127.0.0.1:5000/predict';
    const body = {
      user_id: String(this.text),
      item_id: Number(this.text2),
    };

    this.http.post<General>(`${servicioUrl}`, body).subscribe((resp: any) => {
      this.resultados = resp.prediction;
      localStorage.setItem('resultados', JSON.stringify(this.resultados));
    },
    error => {
      localStorage.setItem('errorMsg', error.message);
    });
  };

  buscarData = (query: string) => {
    query = query.trim();

    const servicioUrl: string = 'http://127.0.0.1:5000/client';
    const body = {
      user_id: String(this.text)
    };

    this.http.post<General>(`${servicioUrl}`, body).subscribe((resp: any) => {
      console.log(resp.data[0]);
      this.data = resp.data;
      console.log(this.data.length);
      localStorage.setItem('data', JSON.stringify(this.data));
    });
  };

  buscar(): void {
    this.text = this.Buscar.nativeElement.value;
    this.text2 = this.BuscarCan.nativeElement.value;

    if (this.text !== '' && this.text2 !== '') {
      this.buscarData(this.text);
      this.buscarPorId(this.text);
      this.BuscarCan.nativeElement.value = '';
      this.Buscar.nativeElement.value = '';
    }
  }
}


