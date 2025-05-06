export interface HealthStatus {
    status: string;
    initialized: boolean;
    sealed: boolean;
    version: string;
  }
  
  export interface SecretList {
    paths: string[];
  }
  
  export interface Secret {
    path: string;
    data: Record<string, string>;
  }