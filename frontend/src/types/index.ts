export interface Trip {
    id: number;
    user_id: number;
    destination: string;
    startDate: string;
    endDate: string;
    budget: number | null;
    status: string;
    itinerary: any | null;
    created_at: string;
    updated_at: string;
}

export interface ChatRequest {
    message: string;
    trip_id?: number;
    user_id?: number;
}

export interface ChatResponse {
    message: string;
    conversation_id: number;
    trip_id?: number;
}
