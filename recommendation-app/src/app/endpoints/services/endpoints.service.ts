import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Data, Prediction } from '../interface/predictions.interface';

@Injectable({
  providedIn: 'root',
})

export class EndpointsService{

  public resultados: Prediction[] = [];
  public data: Data[] = [];


  //Importacion de HttpClient para hacer peticiones HTTP
  constructor(private http: HttpClient) {
    this.resultados = JSON.parse(localStorage.getItem('resultados')!) || [];
    this.data = JSON.parse(localStorage.getItem('data')!) || [];

  }

}
