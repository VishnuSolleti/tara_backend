from django.db.models import F
from django.db.models.functions import Lower
from django.contrib.postgres.search import TrigramSimilarity
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import hsn_codes
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

MIN_CHARS = 2
LIMIT_DEFAULT = 15
LIMIT_MAX = 25
TRGM_THRESHOLD = 0.20  # tune 0.15–0.30


@api_view(["GET"])
@permission_classes([AllowAny])
def hsn_search(request):
    """
    GET /api/hsn/search?q=<query>&limit=15&by=auto
      - by: auto | code | description (default: auto)
      - limit: 1..25 (default: 15)
    Behavior:
      • If q starts with a digit (and by=auto), try code exact+prefix first.
      • Then search description ranked by trigram similarity (lower(description)).
      • Requires at least 2 characters.
    """
    q = (request.GET.get("q") or "").strip()
    by = (request.GET.get("by") or "auto").lower()

    # sanitize limit
    try:
        limit_req = int(request.GET.get("limit", LIMIT_DEFAULT))
    except ValueError:
        limit_req = LIMIT_DEFAULT
    limit = max(1, min(limit_req, LIMIT_MAX))

    if len(q) < MIN_CHARS:
        return Response(
            {"results": [], "message": f"Enter at least {MIN_CHARS} characters."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    results, seen = [], set()

    def push(qs):
        nonlocal results
        for r in qs:
            if r["id"] not in seen:
                seen.add(r["id"])
                results.append(r)
                if len(results) >= limit:
                    break

    looks_numeric = q[0].isdigit()
    want_code = (by == "code") or (by == "auto" and looks_numeric)
    want_desc = (by == "description") or (by == "auto")

    # 1) Code exact + prefix (uses text_pattern_ops index)
    if want_code and len(results) < limit:
        exact_qs = (
            hsn_codes.objects.only("id", "code", "description")
            .filter(code=q)
            .values("id", "code", "description")
        )
        push(exact_qs)

        if len(results) < limit:
            prefix_qs = (
                hsn_codes.objects.only("id", "code", "description")
                .filter(code__startswith=q)
                .exclude(code=q)
                .order_by("code")
                .values("id", "code", "description")[: (limit - len(results))]
            )
            push(prefix_qs)

    # 2) Description search (lower(description) + trigram rank)
    if want_desc and len(results) < limit:
        ql = q.lower()
        desc_qs = (
            hsn_codes.objects.only("id", "code", "description")
            .annotate(desc_lower=Lower("description"))
            .annotate(sim=TrigramSimilarity("desc_lower", ql))
            .filter(desc_lower__icontains=ql)
            .filter(sim__gte=TRGM_THRESHOLD)
            .order_by(F("sim").desc(), "code")
            .values("id", "code", "description")[: (limit - len(results))]
        )
        push(desc_qs)

    return Response({"q": q, "count": len(results), "results": results})
