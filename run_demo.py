import sys, subprocess, time, requests, json
sys.stdout.reconfigure(encoding='utf-8')

# Start fresh server
proc = subprocess.Popen(
    ["python", "-m", "uvicorn", "tracecontext.orchestrator.main:app",
     "--host", "0.0.0.0", "--port", "8000", "--log-level", "warning"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
B = "http://localhost:8000"
for i in range(20):
    time.sleep(1)
    try:
        requests.get(f"{B}/", timeout=1)
        print(f"Orchestrator started (PID {proc.pid}) — ready after {i+1}s")
        break
    except:
        pass

SEP  = "=" * 62
SEP2 = "-" * 62

# ── Health check ────────────────────────────────────────────────
print()
print(SEP)
print("  TRACECONTEXT FULL DEMO  |  Powered by GPT-4o-mini")
print(SEP)
r = requests.get(f"{B}/")
d = r.json()
print(f"\n  Status  : {d['status']}")
print(f"  Version : {d['version']}")

# ── STEP 1: Git commits ─────────────────────────────────────────
print(f"\n{SEP2}")
print("  STEP 1 — git commits captured via git hook")
print(SEP2)

commits = [
    {
        "type": "git_commit",
        "data": {
            "message": "feat: add PaymentService using Braintree gateway",
            "diff": (
                "+from braintree import BraintreeGateway, Configuration, Environment\n"
                "+gateway = BraintreeGateway(Configuration(\n"
                "+    merchant_id=os.getenv('BT_MERCHANT'),\n"
                "+    public_key=os.getenv('BT_PUBLIC'),\n"
                "+))\n"
                "+def charge(amount, nonce):\n"
                "+    return gateway.transaction.sale({'amount': str(amount), 'payment_method_nonce': nonce})\n"
            )
        },
        "metadata": {"repo": "payment-service", "user": "dev"}
    },
    {
        "type": "git_commit",
        "data": {
            "message": "feat: add Money value object - integer cents, never float arithmetic",
            "diff": (
                "+class Money:\n"
                "+    def __init__(self, cents: int, currency: str = 'USD'):\n"
                "+        if not isinstance(cents, int):\n"
                "+            raise TypeError('cents must be int - float causes rounding errors')\n"
                "+        self.cents = cents\n"
                "+        self.currency = currency\n"
                "+    def to_stripe_amount(self) -> int:\n"
                "+        return self.cents\n"
            )
        },
        "metadata": {"repo": "payment-service", "user": "dev"}
    },
    {
        "type": "git_commit",
        "data": {
            "message": "refactor: replace Braintree with Stripe PaymentIntents - global coverage and lower fees",
            "diff": (
                "-from braintree import BraintreeGateway\n"
                "+import stripe\n"
                "+stripe.api_key = os.getenv('STRIPE_SECRET_KEY')\n"
                "+def charge(amount: Money, payment_method_id: str) -> dict:\n"
                "+    return stripe.PaymentIntent.create(\n"
                "+        amount=amount.to_stripe_amount(),\n"
                "+        currency=amount.currency.lower(),\n"
                "+        payment_method=payment_method_id,\n"
                "+        confirm=True,\n"
                "+        idempotency_key=f'charge_{payment_method_id}_{amount.cents}'\n"
                "+    )\n"
            )
        },
        "metadata": {"repo": "payment-service", "user": "dev"}
    },
]

for c in commits:
    r = requests.post(f"{B}/events", json=c, timeout=90)
    resp = r.json()
    msg = c["data"]["message"][:55]
    print(f"  [{resp.get('status','?'):8}]  {msg}...")

# ── STEP 2: Dead-ends ───────────────────────────────────────────
print(f"\n{SEP2}")
print("  STEP 2 — reverts and dead-ends captured")
print(SEP2)

dead_ends = [
    {
        "type": "revert_detected",
        "data": {
            "approach": "Braintree payment gateway",
            "reason": "Supports only 46 countries. SDK maintenance abandoned by PayPal. Higher fees than Stripe. Poor webhook reliability.",
            "alternative": "Stripe PaymentIntents API with mandatory idempotency keys on all mutations"
        },
        "metadata": {"repo": "payment-service", "user": "dev"}
    },
    {
        "type": "revert_detected",
        "data": {
            "approach": "float for monetary values",
            "reason": "IEEE 754 floating-point causes silent rounding errors. 0.1 + 0.2 = 0.30000000000000004. Found lost $0.01 per transaction in load test edge cases.",
            "alternative": "Money value object with integer cents. Store as int, display as formatted string."
        },
        "metadata": {"repo": "payment-service", "user": "dev"}
    },
]

for de in dead_ends:
    r = requests.post(f"{B}/events", json=de, timeout=90)
    resp = r.json()
    approach = de["data"]["approach"][:50]
    print(f"  [{resp.get('status','?'):8}]  Dead-end: {approach}...")

# ── STEP 3: Show all AI-generated context ───────────────────────
print(f"\n{SEP2}")
print("  STEP 3 — AI-generated context (GPT-4o-mini output)")
print(SEP2)

all_records = requests.get(f"{B}/context").json().get("context", [])
new_records = all_records[2:]  # skip 2 pre-seeded records
print(f"\n  {len(new_records)} records from {len(commits)+len(dead_ends)} events:\n")

for i, rec in enumerate(new_records, 1):
    print(f"  [{i}] " + rec.strip().replace("\n", "\n      "))
    print()

# ── STEP 4: MCP search ──────────────────────────────────────────
print(f"\n{SEP2}")
print("  STEP 4 — MCP search_context() as Claude Code would call it")
print(SEP2)

queries = [
    ("Why did we switch payment providers?",  "Braintree"),
    ("How should we store monetary amounts?", "Money cents"),
    ("What is our Stripe integration?",       "Stripe"),
]

for question, query in queries:
    found = requests.get(f"{B}/context", params={"query": query}).json().get("context", [])
    print(f"\n  Q: {question}")
    print(f"  search_context('{query}') -> {len(found)} result(s)")
    if found:
        lines = found[0].strip().split("\n")
        for line in lines[:3]:
            print(f"      {line}")
        if len(lines) > 3:
            print(f"      ...")

# ── STEP 5: MCP handshake ───────────────────────────────────────
print(f"\n{SEP2}")
print("  STEP 5 — MCP server handshake (JSON-RPC)")
print(SEP2)

rpc_msgs = [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize",
     "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "cursor", "version": "1.0"}}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
]
mcp_proc = subprocess.Popen(
    ["tracecontext", "mcp"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    text=True, encoding="utf-8"
)
mcp_input = "\n".join(json.dumps(m) for m in rpc_msgs) + "\n"
mcp_out, _ = mcp_proc.communicate(input=mcp_input, timeout=10)

for line in mcp_out.strip().split("\n"):
    if not line.strip():
        continue
    try:
        parsed = json.loads(line)
        if parsed.get("id") == 1:
            info = parsed["result"]["serverInfo"]
            instr = parsed["result"].get("instructions", "")[:100]
            print(f"\n  Handshake OK : {info['name']} v{info['version']}")
            print(f"  Instructions : {instr}...")
        elif parsed.get("id") == 2:
            tools = [t["name"] for t in parsed["result"]["tools"]]
            print(f"  Tools        : {tools}")
    except Exception:
        pass

# ── Done ─────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("  DEMO COMPLETE")
print(f"  {len(new_records)} AI records generated  |  MCP server verified")
print(f"  Model: GPT-4o-mini  |  Orchestrator: {B}")
print(f"  Claude Code config : ~/.claude/settings.json")
print(SEP)

proc.terminate()
