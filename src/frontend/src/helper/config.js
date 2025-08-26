const DemoProfiles = [
    {
        "name": "Default - get current time and RAG",
        "description": "Simple demo profile with basic system prompt and toolUse like getDateTime",
        "voiceId": "matthew",
        "systemPrompt": "You are a friend. The user and you will engage in a spoken dialog exchanging the transcripts of a natural real-time conversation. Keep your responses short, generally two or three sentences for chatty scenarios.",
        "toolConfig": {
                "tools": [
                    {
                        "toolSpec": {
                        "name": "getDateTool",
                        "description": "get information about the date and time",
                        "inputSchema": {
                            "json": "{\"type\":\"object\",\"properties\":{},\"required\":[]}"
                        }
                    }
                },
                {
                    "toolSpec": {
                        "name": "getKbTool",
                        "description": "get information about Amazon Nova, Nova Sonic and Amazon foundation models",
                        "inputSchema": {
                        "json": "{\"type\":\"object\",\"properties\":{\"query\":{\"type\":\"string\",\"description\":\"The question about Amazon Nova\"}},\"required\":[]}"
                        }
                    }
                }
            ]
        }
    },
    {
        "name": "MCP - get location",
        "description": "Simple demo profile with basic system prompt and toolUse like getDateTime",
        "voiceId": "matthew",
        "systemPrompt": "You are a friend. The user and you will engage in a spoken dialog exchanging the transcripts of a natural real-time conversation. Keep your responses short, generally two or three sentences for chatty scenarios.",
        "toolConfig": {
            "tools": [
                { "toolSpec": {
                    "name": "getLocationTool",
                    "description": "Search for places, addresses.",
                    "inputSchema": {
                        "json": "{\"type\": \"object\", \"properties\": {\"tool\": {\"type\": \"string\", \"description\": \"The function name to search the location service. One of: search_places\"}, \"query\": {\"type\": \"string\", \"description\": \"The search query to find relevant information\"}}, \"required\": [\"query\"]}"
                    }
                }}
            ]
        }
    },
    {
        "name": "Strands Agents - get weather",
        "description": "Simple demo profile with basic system prompt and toolUse like getDateTime",
        "voiceId": "matthew",
        "systemPrompt": "You are a friend. The user and you will engage in a spoken dialog exchanging the transcripts of a natural real-time conversation. Keep your responses short, generally two or three sentences for chatty scenarios.",
        "toolConfig": {
            "tools": [{
                "toolSpec": {
                    "name": "externalAgent",
                    "description": "Get weather information for specific locations.",
                    "inputSchema": {
                    "json": "{\"type\":\"object\",\"properties\":{\"query\":{\"type\":\"string\",\"description\":\"The search query to find relevant information\"}},\"required\":[\"query\"]}"
                    }
                }
            }
            ]
        }
    },
    {
        "name": "Bedrock Agents - booking",
        "description": "Simple demo profile with basic system prompt and toolUse like getDateTime",
        "voiceId": "matthew",
        "systemPrompt": "You are a friend. The user and you will engage in a spoken dialog exchanging the transcripts of a natural real-time conversation. Keep your responses short, generally two or three sentences for chatty scenarios.",
        "toolConfig": {
            "tools": [
                {
                    "toolSpec": {
                        "name": "getBookingDetails",
                        "description": "Manage bookings and reservations: create, get, update, delete, list, or find bookings by customer name. For update_booking, you can update by booking_id or by customer_name. If booking_id is not provided, all bookings for the given customer_name will be updated.",
                        "inputSchema": {
                        "json": "{\"type\":\"object\",\"properties\":{\"query\":{\"type\":\"string\",\"description\":\"The request about booking, reservation\"}},\"required\":[]}"
                        }
                    }                
                }
            ]
        }
    },
    {
        "name": "Customer Service - Finance",
        "description": "",
        "voiceId": "tiffany",
        "systemPrompt": `You are a helpful customer service assistant for a bank. Follow this structured flow in every interaction:
                ## 1. Greeting
                - Begin with a warm greeting.  
                - Ask for the user’s name.  

                ## 2. Personalization
                - Once collected, use the customer’s name naturally throughout the conversation.  

                ## 3. Inquiry Handling
                - Ask user to provide their account Id for inquries. Do not ask again if they have already provided it.
                - If the customer asks about banking related **account balance**, call the [ac_bank_agent] tool.  
                - If the customer asks a **mortgage-related question**, call the [ac_mortgage_agent] tool. 
                - Do not ask for account Id if user has already provided it. 
                - Do not repeat the ID user provided.
                - For IDs in the format of 123 generate as one two three 

                ## 4. Important notice
                - If the user asks a question unrelated to banking or mortgages, respond with: 'Sorry, I’m unable to assist with that topic. I can help you with banking or mortgage-related inquiries.'
                - Ask for the account ID only once. Do not repeatedly request it for different inquiries.

                ---

                # Example Interaction Flows

                ### Example 1: Account Balance Inquiry

                **Assistant:** Hi! Welcome to Any Bank. May I have your name, please?  
                **User:** I’m Alex.  
                **Assistant:** Thank you, Alex! How can I help you today?  
                **User:** Can you check my balance?  
                **Assistant:** Sure, Alex. I’ll connect you to our banking services to get that information. 
                **Assistant:** May I have your account Id please?
                **User:** My ID is one two three four five.
                call [ac_bank_agent]
                **Assistant:** You have a current balance of USD 1600.00 and pending transactions of USD 56.25.

                ---

                ### Example 2: Mortgage Inquiry
                **User:** I want to know about mortgage refinancing options.  
                **Assistant:** Absolutely, Sarah. I’ll connect you to our mortgage services to get that information.  
                call [ac_mortgage_agent]
            `,
        "toolConfig": {
            "tools": [
                {
                    "toolSpec": {
                        "name": "ac_bank_agent",
                        "description": `Use this tool whenever the customer asks about their **bank account balance** or **bank statement**.  
                                It should be triggered for queries such as:  
                                - "What’s my balance?"  
                                - "How much money do I have in my account?"  
                                - "Can I see my latest bank statement?"  
                                - "Show me my account summary."`,
                        "inputSchema": {
                            "json": JSON.stringify({
                            "type": "object",
                            "properties": {
                                "accountId": {
                                    "type": "string",
                                    "description": "This is a user input. It is the bank account Id which is a numeric number."
                                },
                                "query": {
                                    "type": "string",
                                    "description": "The inquiry to the bank agent such as check account balance, get statement etc."
                                }
                            },
                            "required": [
                                "accountId", "query"
                            ]
                            })
                        }
                    }
                },
                {
                    "toolSpec": {
                        "name": "ac_mortgage_agent",
                        "description": `Use this tool whenever the customer has a **mortgage-related inquiry**.  
                                        It should be triggered for queries such as:  
                                        - "What are the current mortgage rates?"  
                                        - "Can I refinance my mortgage?"  
                                        - "How do I apply for a mortgage?"  
                                        - "Tell me about mortgage repayment options.`,
                        "inputSchema": {
                            "json": JSON.stringify({
                            "type": "object",
                                "properties": {
                                    "accountId": {
                                        "type": "string",
                                        "description": "This is a user input. It is the bank account Id which is a numeric number."
                                    },
                                    "query": {
                                        "type": "string",
                                        "description": "The inquiry to the mortgage agent such as mortgage rates, refinance, bank reference letter, repayment etc."
                                    }
                                },
                                "required": ["accountId", "query"]
                            })
                        }
                    }
                }
            ]
        }
    }
];

const Voices = [
    { label: "Matthew (English US)", value: "matthew" },
    { label: "Tiffany (English US)", value: "tiffany" },
    { label: "Amy (English GB)", value: "amy" },
    { label: "Ambre (French)", value: "ambre" },
    { label: "Florian (French)", value: "florian" },
    { label: "Beatrice (Italian)", value: "beatrice" },
    { label: "Lorenzo (Italian)", value: "lorenzo" },
    { label: "Greta (German)", value: "greta" },
    { label: "Lennart (German)", value: "lennart" },
    { label: "Lupe (Spanish)", value: "lupe"},
    { label: "Carlos (Spanish)", value: "carlos"},
]

export {DemoProfiles, Voices};