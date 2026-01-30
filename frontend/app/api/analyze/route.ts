import { NextResponse } from 'next/server';

export async function POST(request: Request) {
    const formData = await request.formData();


    try {
        const backendResponse = await fetch("http://127.0.0.1:8000/analyze", {
            method: "POST",
            body: formData,
        });

        if (!backendResponse.ok) {
            console.error("Backend Error:", await backendResponse.text());
            return NextResponse.json(
                { status: "error", message: "Failed to communicate with AI Engine" },
                { status: 500 }
            );
        }

        const data = await backendResponse.json();
        return NextResponse.json(data);

    } catch (error) {
        console.error("API Proxy Error:", error);
        return NextResponse.json(
            { status: "error", message: "Frontend API Proxy Failed", details: String(error) },
            { status: 500 }
        );
    }
}
