import { Injectable, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Data, General, Prediction } from '../interface/predictions.interface';

@Injectable({
  providedIn: 'root',
})

export class EndpointsService {

  private apiUrl: string = 'http://ec2-34-202-165-117.compute-1.amazonaws.com:5000';
  public resultados: Prediction[] = [];
  public data: Data[] = [];

  //Importacion de HttpClient para hacer peticiones HTTP
  constructor(private http: HttpClient) {
    this.resultados = JSON.parse(localStorage.getItem('resultados')!) || [];
    this.data = JSON.parse(localStorage.getItem('data')!) || [];
  }


  buscarPorId = (query: string, q: string) => {
    query = query.trim();
    q = q.trim();

    const servicioUrl: string = `${this.apiUrl}/predict`;
    const body = {
      user_id: String(query),
      item_id: Number(q),
    };

    this.http.post<General>(`${servicioUrl}`, body).subscribe((resp: any) => {
      this.resultados = resp.prediction;
      localStorage.setItem('resultados', JSON.stringify(this.resultados));
    },
    error => {
      console.log(error.message);
    });
  };

  buscarData = (query: string) => {
    query = query.trim();

    const servicioUrl: string = `${this.apiUrl}/client`;
    const body = {
      user_id: String(query)
    };

    this.http.post<General>(`${servicioUrl}`, body).subscribe((resp: any) => {
      this.data = resp.data;
      localStorage.setItem('data', JSON.stringify(this.data));
    },
    error => {
      console.log(error.message);
    });
  };
}
