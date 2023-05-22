import { Injectable} from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Data, General, Prediction, PredictionC } from '../interface/predictions.interface';

@Injectable({
  providedIn: 'root',
})

export class EndpointsService {

  private apiUrl: string = 'http://ec2-34-202-165-117.compute-1.amazonaws.com:5000';
  // private apiUrl: string = 'http://127.0.0.1:5000';
  public resultados: Prediction[] = [];
  // public resultadosC: PredictionC[] = [];
  public data: Data[] = [];
  public errorMsg = 'error';

  //Importacion de HttpClient para hacer peticiones HTTP
  constructor(private http: HttpClient) {
    this.resultados = JSON.parse(localStorage.getItem('resultados')!) || [];
    // this.resultadosC = JSON.parse(localStorage.getItem('resultadosC')!) || [];
    this.data = JSON.parse(localStorage.getItem('data')!) || [];
    this.errorMsg = 'error';
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
      this.errorMsg = 'error';
    },
    error => {
      this.errorMsg = "Error";
    });
  };

  // buscarCollab = (query: string, q: string) => {
  //   query = query.trim();
  //   q = q.trim();
  //   const servicioUrl: string = `${this.apiUrl}/collab_predict`;
  //   const body = {
  //     user_id: String(query),
  //     item_id: Number(q),
  //   };
  //   this.http.post<General>(`${servicioUrl}`, body).subscribe((resp: any) => {
  //     this.resultadosC = resp.prediction;
  //     localStorage.setItem('resultadosC', JSON.stringify(this.resultadosC));
  //   },
  //   error => {
  //     this.errorMsg = "Error";
  //   });
  // }

  buscarData = (query: string) => {
    query = query.trim();

    const servicioUrl: string = `${this.apiUrl}/client`;
    const body = {
      user_id: String(query)
    };

    this.http.post<General>(`${servicioUrl}`, body).subscribe((resp: any) => {
      this.data = resp.data;
      localStorage.setItem('data', JSON.stringify(this.data));
      this.errorMsg = 'error';
    },
    error => {
      this.errorMsg = "Error";
    });
  };

  entrenar = () => {
    const servicioUrl: string = `${this.apiUrl}/train`;
    this.http.post<General>(`${servicioUrl}`, {}).subscribe((resp: any) => {
      console.log(this.errorMsg);
    });
  }
}
