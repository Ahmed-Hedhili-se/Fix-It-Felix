export interface AnalysisResponse {
    incident_id: string;
    status: string;
    analysis: {
        detected_issues: string;
        severity: string;
        problem_description: string;
        repair_solution: string;
    };
    knowledge_base: {
        found_match: boolean;
        confidence_score: number;
        reference_solution: string;
        document_ref: string;
    };
}


export type OperationMode = 'cloud' | 'local' | 'fast';

export async function analyzeImage(image: File | null, context: string, mode: OperationMode): Promise<AnalysisResponse> {
    const formData = new FormData();
    if (image) {
        formData.append('image', image);
    }
    formData.append('context', context);
    formData.append('mode', mode);


    const res = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
    });

    if (!res.ok) {
        throw new Error('Analysis failed');
    }

    return res.json();
}
