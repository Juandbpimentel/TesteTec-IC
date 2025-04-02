import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: baseURL,
  timeout: 10000,
});

export const fetchOperadoras = async (params = {}, options = {}) => {
  try {
    const response = await api.get('/operadoras/', { params, ...options });
    return response;
  } catch (error) {
    console.error('Erro ao buscar operadoras:', error);
    throw error;
  }
};

export const fetchMaioresDespesasTrimestre = async (params = {}, options = {}) => {
  try {
    const response = await api.get('/operadoras/maiores_despesas_trimestre', { params, ...options });
    return response;
  } catch (error) {
    console.error('Erro ao buscar maiores despesas no trimestre:', error);
    throw error;
  }
};

export const fetchMaioresDespesasAno = async (params = {}, options = {}) => {
  try {
    const response = await api.get('/operadoras/maiores_despesas_ano', { params, ...options });
    return response;
  } catch (error) {
    console.error('Erro ao buscar maiores despesas no ano:', error);
    throw error;
  }
};

export const fetchUfs = async (options = {}) => {
  try {
    const response = await api.get('/operadoras/select_ufs', options);
    return response;
  } catch (error) {
    console.error('Erro ao buscar UFs:', error);
    throw error;
  }
};

export const fetchModalidades = async (options = {}) => {
  try {
    const response = await api.get('/operadoras/select_modalidades', options);
    return response;
  } catch (error) {
    console.error('Erro ao buscar modalidades:', error);
    throw error;
  }
};

export const fetchOperadoraByRegistro = async (registroOperadora, options = {}) => {
  try {
    const response = await api.get(`/operadoras/${registroOperadora}`, options);
    return response;
  } catch (error) {
    console.error(`Erro ao buscar operadora com registro ${registroOperadora}:`, error);
    throw error;
  }
};

export const fetchDemonstracoes = async (params = {}, options = {}) => {
  try {
    const response = await api.get('/demonstracoes/', { params, ...options });
    return response;
  } catch (error) {
    console.error('Erro ao buscar demonstrações contábeis:', error);
    throw error;
  }
};

export const fetchDescricoesDemonstracoes = async (options = {}) => {
  try {
    const response = await api.get('/demonstracoes/select_descricoes', options);
    return response;
  } catch (error) {
    console.error('Erro ao buscar descrições das demonstrações contábeis:', error);
    throw error;
  }
};

export const fetchTrimestresEAnos = async (options = {}) => {
  try {
    const response = await api.get('/demonstracoes/select_trimestres_e_anos', options);
    return response;
  } catch (error) {
    console.error('Erro ao buscar trimestres e anos das demonstrações contábeis:', error);
    throw error;
  }
};

export const fetchDemonstracaoById = async (id, options = {}) => {
  try {
    const response = await api.get(`/demonstracoes/${id}`, options);
    return response;
  } catch (error) {
    console.error(`Erro ao buscar demonstração contábil com ID ${id}:`, error);
    throw error;
  }
};

export default api;