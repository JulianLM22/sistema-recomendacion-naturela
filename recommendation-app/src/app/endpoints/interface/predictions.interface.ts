export interface General{
  prediction: Prediction[];
  predictionC: PredictionC[];
  data: Data[];
}

export interface Prediction {
  codigo_pt: string;
  est: number;
  producto_terminado: string;
  id_pt: number;
}
export interface PredictionC {
  categoria:          null;
  codigo_pt:          string;
  id_pt:              number;
  num_pt:             number;
  producto_terminado: string;
  puntaje:            number;
}
export interface Data {
  ciudad:         string;
  departamento:   string;
  id:             number;
  id_cliente:     string;
  naturaleza:     string;
  nombre_cliente: string;
  nombre_est:     string;
  pais:           string;
  tipo_cliente:   string;
  tipo_id:        string;
  tipo_persona:   string;
}

