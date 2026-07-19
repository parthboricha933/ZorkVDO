import { NextRequest, NextResponse } from "next/server";

/**
 * API proxy — forwards all /api/v1/* requests to the Railway backend.
 *
 * This solves two problems:
 * 1. DNS issues — some ISPs/users can't resolve *.up.railway.app directly.
 *    Vercel's servers can, so we proxy through them.
 * 2. CORS — same-origin requests (vercel.app → vercel.app) don't need CORS.
 *
 * The backend URL is set via BACKEND_URL env var on Vercel (server-side only,
 * not exposed to the browser).
 */

const BACKEND_URL =
  process.env.BACKEND_URL || "https://zorkvdo-production.up.railway.app";

async function handler(
  req: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const { path } = await params;
  const pathStr = path.join("/");
  const url = new URL(req.url);
  const search = url.search;

  // Build the target URL
  const targetUrl = `${BACKEND_URL}/api/v1/${pathStr}${search}`;

  // Clone request headers
  const headers = new Headers(req.headers);
  // Remove host header (Vercel will set its own)
  headers.delete("host");
  headers.delete("connection");
  // Remove x-forwarded headers to avoid conflicts
  headers.delete("x-forwarded-for");
  headers.delete("x-forwarded-host");
  headers.delete("x-forwarded-proto");

  // Handle request body
  let body: BodyInit | null = null;
  if (req.method !== "GET" && req.method !== "HEAD") {
    if (req.headers.get("content-type")?.includes("multipart/form-data")) {
      // For file uploads, pass the body as-is
      body = req.body;
    } else {
      body = await req.text();
    }
  }

  try {
    const resp = await fetch(targetUrl, {
      method: req.method,
      headers,
      body,
      // @ts-expect-error — duplex is needed for streaming bodies
      duplex: "half",
    });

    // Forward the response
    const respHeaders = new Headers(resp.headers);
    // Add CORS header for same-origin requests
    respHeaders.set("Access-Control-Allow-Origin", "*");
    respHeaders.delete("content-encoding"); // Vercel handles compression

    const respBody = await resp.arrayBuffer();
    return new NextResponse(respBody, {
      status: resp.status,
      statusText: resp.statusText,
      headers: respHeaders,
    });
  } catch (e) {
    const error = e as Error;
    return NextResponse.json(
      {
        error: {
          code: "proxy_error",
          message: error.message || "Failed to reach backend",
          details: { targetUrl: targetUrl.replace(/\/api\/v1.*/, "") },
        },
      },
      { status: 502 }
    );
  }
}

export {
  handler as GET,
  handler as POST,
  handler as PUT,
  handler as PATCH,
  handler as DELETE,
  handler as OPTIONS,
  handler as HEAD,
};
