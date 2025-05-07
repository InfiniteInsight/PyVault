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
    secretPath?: string;
    secretKey?: string;
    secretValue?: string;
    data?: Record<string, string>;
  }