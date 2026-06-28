import { NextRequest, NextResponse } from "next/server";

const backendBaseUrl = () => process.env.BACKEND_API_BASE_URL ?? "http://127.0.0.1:8001";

type RouteContext = {
  params: Promise<{
    ticker: string;
  }>;
};

export async function GET(_request: NextRequest, context: RouteContext) {
  const { ticker } = await context.params;
  const upstreamUrl = `${backendBaseUrl()}/api/research/company/${encodeURIComponent(ticker)}`;

  try {
    const upstream = await fetch(upstreamUrl, {
      cache: "no-store",
      headers: {
        accept: "application/json"
      }
    });
    const body = await upstream.text();
    return new NextResponse(body, {
      status: upstream.status,
      headers: {
        "content-type": upstream.headers.get("content-type") ?? "application/json"
      }
    });
  } catch (error) {
    return NextResponse.json(
      {
        detail:
          error instanceof Error
            ? `Backend research API unavailable: ${error.message}`
            : "Backend research API unavailable"
      },
      { status: 502 }
    );
  }
}
