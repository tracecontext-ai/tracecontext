import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
    CallToolRequestSchema,
    ListToolsRequestSchema,
    ListResourcesRequestSchema,
    ReadResourceRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";
import { z } from "zod";

const ORCHESTRATOR_URL = process.env.ORCHESTRATOR_URL || "http://localhost:8000";

const server = new Server(
    {
        name: "tracecontext-server",
        version: "1.0.0",
    },
    {
        capabilities: {
            resources: {},
            tools: {},
        },
    }
);

/**
 * List available resources.
 */
server.setRequestHandler(ListResourcesRequestSchema, async () => {
    return {
        resources: [
            {
                uri: "tracecontext://active-context",
                name: "Active Persistent Context",
                mimeType: "text/markdown",
                description: "The most relevant context for the current session.",
            },
        ],
    };
});

/**
 * Read active context.
 */
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
    if (request.params.uri === "tracecontext://active-context") {
        try {
            const response = await axios.get(`${ORCHESTRATOR_URL}/context?query=active_session`);
            return {
                contents: [
                    {
                        uri: request.params.uri,
                        mimeType: "text/markdown",
                        text: response.data.context.join("\n\n") || "No persistent context found.",
                    },
                ],
            };
        } catch (error) {
            throw new Error("Failed to fetch context from orchestrator.");
        }
    }
    throw new Error("Resource not found");
});

/**
 * List available tools.
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
        tools: [
            {
                name: "get_relevant_context",
                description: "Fetch context chunks relevant to a specific task or query.",
                inputSchema: {
                    type: "object",
                    properties: {
                        query: { type: "string" },
                    },
                    required: ["query"],
                },
            },
        ],
    };
});

/**
 * Handle tool calls.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    if (request.params.name === "get_relevant_context") {
        const { query } = z.object({ query: z.string() }).parse(request.params.arguments);
        try {
            const response = await axios.get(`${ORCHESTRATOR_URL}/context?query=${encodeURIComponent(query)}`);
            return {
                content: [
                    {
                        type: "text",
                        text: response.data.context.join("\n\n") || "No relevant context found.",
                    },
                ],
            };
        } catch (error) {
            return {
                content: [{ type: "text", text: "Error fetching context." }],
                isError: true,
            };
        }
    }
    throw new Error("Tool not found");
});

const transport = new StdioServerTransport();
await server.connect(transport);
