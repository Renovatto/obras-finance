/**
 * API Utility - Centralizes backend communication.
 * Base URL: /api/v1 (Relative for portability)
 */

const BASE_URL = '/api/v1';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
	const url = `${BASE_URL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
	
	const headers = {
		'Content-Type': 'application/json',
		...options.headers
	};

	try {
		const response = await fetch(url, { ...options, headers });
		
		if (!response.ok) {
			const errorData = await response.json().catch(() => ({}));
			throw new Error(errorData.detail || `Request failed with status ${response.status}`);
		}

		if (response.status === 204) return {} as T;
		return await response.json();
	} catch (error) {
		console.error(`[API Error] ${url}:`, error);
		throw error;
	}
}

export const api = {
	get: <T>(url: string, options?: RequestInit) => request<T>(url, { ...options, method: 'GET' }),
	post: <T>(url: string, body: any, options?: RequestInit) => 
		request<T>(url, { ...options, method: 'POST', body: JSON.stringify(body) }),
	put: <T>(url: string, body: any, options?: RequestInit) => 
		request<T>(url, { ...options, method: 'PUT', body: JSON.stringify(body) }),
	patch: <T>(url: string, body: any, options?: RequestInit) => 
		request<T>(url, { ...options, method: 'PATCH', body: JSON.stringify(body) }),
	delete: <T>(url: string, options?: RequestInit) => 
		request<T>(url, { ...options, method: 'DELETE' })
};
