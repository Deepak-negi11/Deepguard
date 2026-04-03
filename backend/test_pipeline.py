import json
import math
import sys
import time

import httpx

API_URL = "http://localhost:8000/api/v1"


def assert_valid_result(result: dict, mode: str):
    """Sanity assertions — not just schema, but result quality."""
    assert "authenticity_score" in result, "Missing authenticity_score"
    assert "verdict" in result, "Missing verdict"
    assert "confidence" in result, "Missing confidence"

    confidence = result["confidence"]
    assert isinstance(confidence, (int, float)), f"confidence is not a number: {confidence}"
    assert not math.isnan(confidence), "confidence is NaN"
    assert 0.0 <= confidence <= 1.0, f"confidence out of range: {confidence}"

    authenticity = result["authenticity_score"]
    assert isinstance(authenticity, (int, float)), f"authenticity_score is not a number: {authenticity}"
    assert not math.isnan(authenticity), "authenticity_score is NaN"
    assert 0.0 <= authenticity <= 1.0, f"authenticity_score out of range: {authenticity}"

    verdict = result["verdict"]
    assert verdict in ("likely fake", "likely real", "uncertain"), f"Invalid verdict: {verdict}"

    print(f"  ✓ Confidence: {confidence:.3f}")
    print(f"  ✓ Authenticity: {authenticity:.3f}")
    print(f"  ✓ Verdict: {verdict}")
    print(f"  ✓ All sanity checks passed for {mode} analysis")


def test_image_analysis(client, headers):
    """Upload an image and verify the ML pipeline returns valid results."""
    print("\n=== IMAGE ANALYSIS TEST ===")
    print("Uploading image to /verify/image...")

    file_path = "chatgpt.png"
    files = {'file': ('fake_image.png', open(file_path, 'rb'), 'image/png')}
    resp = client.post(f"{API_URL}/verify/image", headers=headers, files=files)

    if resp.status_code != 202:
        print(f"Upload failed: {resp.status_code} - {resp.text}")
        return False

    task_id = resp.json()["task_id"]
    print(f"Image queued. Task ID: {task_id}")

    return poll_for_result(client, headers, task_id, "image")


def test_news_analysis(client, headers):
    """Submit news text and verify the ML pipeline returns valid results."""
    print("\n=== NEWS ANALYSIS TEST ===")
    print("Submitting news text to /verify/news...")

    payload = {
        "text": "BREAKING: Scientists discover that the moon is actually made of cheese. NASA confirms this shocking finding after a secret mission revealed dairy products beneath the lunar surface.",
        "url": None,
    }
    resp = client.post(f"{API_URL}/verify/news", headers=headers, json=payload)

    if resp.status_code not in (200, 202):
        print(f"News submit failed: {resp.status_code} - {resp.text}")
        return False

    data = resp.json()
    task_id = data.get("task_id")
    if not task_id:
        print(f"No task_id in response: {data}")
        return False

    print(f"News queued. Task ID: {task_id}")
    return poll_for_result(client, headers, task_id, "news")


def poll_for_result(client, headers, task_id, mode):
    """Poll until task completes, then validate the result."""
    print("Polling for results...")
    for i in range(30):
        time.sleep(2)
        resp = client.get(f"{API_URL}/results/{task_id}", headers=headers)
        if resp.status_code != 200:
            print(f"  Polling error: {resp.text}")
            continue

        data = resp.json()
        status = data.get("status")
        print(f"  [{i*2}s] Status={status} | Step={data.get('current_step', '')} | Progress={data.get('progress')}%")

        if status == "completed":
            result = data.get("result", {})
            print(f"\n  ==== {mode.upper()} RESULT ====")
            print(json.dumps(result, indent=2))
            assert_valid_result(result, mode)
            return True
        elif status == "failed":
            print(f"  Task FAILED: {data}")
            return False

    print("  Timeout.")
    return False


def main():
    with httpx.Client(timeout=120.0) as client:
        # Auth
        # Auth
        email = f"test_{int(time.time())}@example.com"
        pwd = "password123"
        print(f"Registering {email}...")
        resp = client.post(f"{API_URL}/auth/register", json={"email": email, "password": pwd})
        if resp.status_code not in (200, 201):
            print(f"Register response: {resp.text}, attempting login anyway...")

        resp = client.post(f"{API_URL}/auth/login", json={"email": email, "password": pwd})
        if resp.status_code != 200:
            print(f"Login failed: {resp.text}")
            sys.exit(1)

        token = resp.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        csrf = client.cookies.get("deepguard_csrf")
        if csrf:
            headers["X-CSRF-Token"] = csrf

        print("Logged in successfully.\n")

        # Run tests
        image_ok = test_image_analysis(client, headers)
        news_ok = test_news_analysis(client, headers)

        print("\n=== SUMMARY ===")
        print(f"Image: {'✓ PASS' if image_ok else '✗ FAIL'}")
        print(f"News:  {'✓ PASS' if news_ok else '✗ FAIL'}")

        sys.exit(0 if image_ok and news_ok else 1)


if __name__ == "__main__":
    main()
