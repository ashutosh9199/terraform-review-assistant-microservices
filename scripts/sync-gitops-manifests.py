"""Refresh kubernetes/gitops/<service>/{deployment,service}.yaml from the live
cluster state. Run this after a real deploy.yml deploy changes an image tag
(or after a redeploy changes ClusterIPs/nodePorts) to bring the per-service
ArgoCD Applications in argocd/production-*.yaml back to Synced. Commit and
push the result -- ArgoCD reads from the git repo, not local disk.
"""
import os
import subprocess

import yaml

SERVICES = [
    "api-gateway", "frontend", "upload-service", "parser-service",
    "rules-service", "ai-review-service", "scoring-service", "reporting-service",
]

BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kubernetes", "gitops")


def clean(obj):
    obj["metadata"].pop("creationTimestamp", None)
    obj["metadata"].pop("resourceVersion", None)
    obj["metadata"].pop("uid", None)
    obj["metadata"].pop("generation", None)
    obj["metadata"].pop("managedFields", None)
    obj["metadata"].pop("selfLink", None)
    obj["metadata"].pop("annotations", None)
    obj.pop("status", None)
    return obj


def dump(kind, name):
    raw = subprocess.run(
        ["kubectl", "get", kind, name, "-n", "production", "-o", "yaml"],
        capture_output=True, text=True, check=True,
    ).stdout
    return clean(yaml.safe_load(raw))


for svc in SERVICES:
    out_dir = os.path.join(BASE, svc)
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "deployment.yaml"), "w", newline="\n") as f:
        yaml.safe_dump(dump("deployment", svc), f, default_flow_style=False, sort_keys=False)

    with open(os.path.join(out_dir, "service.yaml"), "w", newline="\n") as f:
        yaml.safe_dump(dump("service", svc), f, default_flow_style=False, sort_keys=False)

    print(f"wrote {svc}")
