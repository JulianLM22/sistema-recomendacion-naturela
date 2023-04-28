export interface General{
  prediction: Prediction[];
  data: Data[];
}

export interface Prediction {
  codigo_pt: string;
  est: number;
  producto_terminado: string;
  pt_id: number;
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
