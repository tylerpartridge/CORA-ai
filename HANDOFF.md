# CORA — Ops Handoff (2025-08-18)

Good state:
- App on :8000 OK, nginx :80/:443 OK, Cloudflare OK
- HEAD / → 200, HEAD /expenses → 200, GET /healthz → {"ok": true}

Quick verify (run these if anything looks off):
ss -ltnp | egrep '(:8000 )|(:80 )|(:443 )' || true
curl -sSI http://127.0.0.1:8000/ | head -1
curl -sS  http://127.0.0.1:8000/healthz ; echo
curl -sSI http://127.0.0.1/ | head -1
curl -sSI http://127.0.0.1/expenses | head -1
curl -sSI https://coraai.tech/ | head -1
curl -sSI https://coraai.tech/expenses | head -1


---
**Latest checkpoint**: ckpt-20250823-203912 at 2025-08-23T20:39:12.544262Z


---
**Latest checkpoint**: ckpt-20250823-204408 at 2025-08-23T20:44:08.160729Z


---
**Latest checkpoint**: ckpt-20250823-204415 at 2025-08-23T20:44:15.383984Z


---
**Latest checkpoint**: ckpt-20250823-204737 at 2025-08-23T20:47:37.401275Z


---
**Latest checkpoint**: ckpt-20250823-204857 at 2025-08-23T20:48:57.551333Z


---
**Latest checkpoint**: ckpt-20250823-205616 at 2025-08-23T20:56:16.136473+00:00Z


---
**Latest checkpoint**: ckpt-20250823-205800 at 2025-08-23T20:58:00.922545+00:00Z


---
**Latest checkpoint**: ckpt-20250823-205927 at 2025-08-23T20:59:27.677532+00:00Z


---
**Latest checkpoint**: ckpt-20250823-205940 at 2025-08-23T20:59:40.118494+00:00Z


---
**Latest checkpoint**: ckpt-20250823-211434 at 2025-08-23T21:14:34.722898+00:00Z


---
**Latest checkpoint**: ckpt-20250823-212937 at 2025-08-23T21:29:37.759345+00:00Z


---
**Latest checkpoint**: ckpt-20250823-214452 at 2025-08-23T21:44:52.859832+00:00Z


---
**Latest checkpoint**: ckpt-20250823-220004 at 2025-08-23T22:00:04.811477+00:00Z


---
**Latest checkpoint**: ckpt-20250823-220549 at 2025-08-23T22:05:49.241714+00:00Z


---
**Latest checkpoint**: ckpt-20250823-221518 at 2025-08-23T22:15:18.654390+00:00Z


---
**Latest checkpoint**: ckpt-20250823-223026 at 2025-08-23T22:30:27.059198+00:00Z


---
**Latest checkpoint**: ckpt-20250823-224527 at 2025-08-23T22:45:27.705902+00:00Z


---
**Latest checkpoint**: ckpt-20250823-230052 at 2025-08-23T23:00:52.798471+00:00Z


---
**Latest checkpoint**: ckpt-20250823-231553 at 2025-08-23T23:15:53.139777+00:00Z


---
**Latest checkpoint**: ckpt-20250823-233054 at 2025-08-23T23:30:54.680783+00:00Z


---
**Latest checkpoint**: ckpt-20250823-234607 at 2025-08-23T23:46:07.541831+00:00Z


---
**Latest checkpoint**: ckpt-20250824-000125 at 2025-08-24T00:01:25.824023+00:00Z


---
**Latest checkpoint**: ckpt-20250824-001627 at 2025-08-24T00:16:27.741143+00:00Z


---
**Latest checkpoint**: ckpt-20250824-003207 at 2025-08-24T00:32:07.748350+00:00Z


---
**Latest checkpoint**: ckpt-20250824-004727 at 2025-08-24T00:47:27.750300+00:00Z


---
**Latest checkpoint**: ckpt-20250824-010237 at 2025-08-24T01:02:37.751325+00:00Z


---
**Latest checkpoint**: ckpt-20250824-011757 at 2025-08-24T01:17:57.777683+00:00Z


---
**Latest checkpoint**: ckpt-20250824-013307 at 2025-08-24T01:33:07.731450+00:00Z


---
**Latest checkpoint**: ckpt-20250824-014827 at 2025-08-24T01:48:27.711494+00:00Z


---
**Latest checkpoint**: ckpt-20250824-020347 at 2025-08-24T02:03:47.749446+00:00Z


---
**Latest checkpoint**: ckpt-20250824-021911 at 2025-08-24T02:19:11.305865+00:00Z


---
**Latest checkpoint**: ckpt-20250824-023425 at 2025-08-24T02:34:26.018403+00:00Z


---
**Latest checkpoint**: ckpt-20250824-024927 at 2025-08-24T02:49:27.804964+00:00Z


---
**Latest checkpoint**: ckpt-20250824-030507 at 2025-08-24T03:05:07.769801+00:00Z


---
**Latest checkpoint**: ckpt-20250824-032017 at 2025-08-24T03:20:17.769150+00:00Z


---
**Latest checkpoint**: ckpt-20250824-033527 at 2025-08-24T03:35:27.719150+00:00Z


---
**Latest checkpoint**: ckpt-20250824-035027 at 2025-08-24T03:50:27.800036+00:00Z


---
**Latest checkpoint**: ckpt-20250824-040607 at 2025-08-24T04:06:07.705675+00:00Z


---
**Latest checkpoint**: ckpt-20250824-042116 at 2025-08-24T04:21:16.869383+00:00Z


---
**Latest checkpoint**: ckpt-20250824-043627 at 2025-08-24T04:36:27.696482+00:00Z


---
**Latest checkpoint**: ckpt-20250824-045130 at 2025-08-24T04:51:30.496120+00:00Z


---
**Latest checkpoint**: ckpt-20250824-050635 at 2025-08-24T05:06:35.661521+00:00Z


---
**Latest checkpoint**: ckpt-20250824-052137 at 2025-08-24T05:21:37.682777+00:00Z


---
**Latest checkpoint**: ckpt-20250824-053639 at 2025-08-24T05:36:39.295290+00:00Z


---
**Latest checkpoint**: ckpt-20250824-055142 at 2025-08-24T05:51:42.187317+00:00Z


---
**Latest checkpoint**: ckpt-20250824-060647 at 2025-08-24T06:06:47.409217+00:00Z


---
**Latest checkpoint**: ckpt-20250824-062147 at 2025-08-24T06:21:47.709120+00:00Z


---
**Latest checkpoint**: ckpt-20250824-063657 at 2025-08-24T06:36:57.703644+00:00Z


---
**Latest checkpoint**: ckpt-20250824-065217 at 2025-08-24T06:52:17.764374+00:00Z


---
**Latest checkpoint**: ckpt-20250824-070727 at 2025-08-24T07:07:27.719834+00:00Z


---
**Latest checkpoint**: ckpt-20250824-072255 at 2025-08-24T07:22:55.872738+00:00Z


---
**Latest checkpoint**: ckpt-20250824-073758 at 2025-08-24T07:37:58.876015+00:00Z


---
**Latest checkpoint**: ckpt-20250824-075317 at 2025-08-24T07:53:17.732230+00:00Z


---
**Latest checkpoint**: ckpt-20250824-080827 at 2025-08-24T08:08:27.786910+00:00Z


---
**Latest checkpoint**: ckpt-20250824-082357 at 2025-08-24T08:23:57.723347+00:00Z


---
**Latest checkpoint**: ckpt-20250824-083927 at 2025-08-24T08:39:27.776440+00:00Z


---
**Latest checkpoint**: ckpt-20250824-085433 at 2025-08-24T08:54:34.043612+00:00Z


---
**Latest checkpoint**: ckpt-20250824-090936 at 2025-08-24T09:09:37.019952+00:00Z


---
**Latest checkpoint**: ckpt-20250824-092501 at 2025-08-24T09:25:01.779977+00:00Z


---
**Latest checkpoint**: ckpt-20250824-094001 at 2025-08-24T09:40:01.838453+00:00Z


---
**Latest checkpoint**: ckpt-20250824-095527 at 2025-08-24T09:55:27.718276+00:00Z


---
**Latest checkpoint**: ckpt-20250824-101033 at 2025-08-24T10:10:33.590213+00:00Z


---
**Latest checkpoint**: ckpt-20250824-102545 at 2025-08-24T10:25:45.193498+00:00Z


---
**Latest checkpoint**: ckpt-20250824-104056 at 2025-08-24T10:40:56.865007+00:00Z


---
**Latest checkpoint**: ckpt-20250824-105557 at 2025-08-24T10:55:57.710896+00:00Z


---
**Latest checkpoint**: ckpt-20250824-111107 at 2025-08-24T11:11:07.706950+00:00Z


---
**Latest checkpoint**: ckpt-20250824-112609 at 2025-08-24T11:26:09.205262+00:00Z


---
**Latest checkpoint**: ckpt-20250824-114113 at 2025-08-24T11:41:13.933472+00:00Z


---
**Latest checkpoint**: ckpt-20250824-115627 at 2025-08-24T11:56:27.682357+00:00Z


---
**Latest checkpoint**: ckpt-20250824-121131 at 2025-08-24T12:11:31.194871+00:00Z


---
**Latest checkpoint**: ckpt-20250824-122641 at 2025-08-24T12:26:41.200958+00:00Z


---
**Latest checkpoint**: ckpt-20250824-124157 at 2025-08-24T12:41:57.726021+00:00Z


---
**Latest checkpoint**: ckpt-20250824-125707 at 2025-08-24T12:57:07.705388+00:00Z


---
**Latest checkpoint**: ckpt-20250824-131227 at 2025-08-24T13:12:27.704247+00:00Z


---
**Latest checkpoint**: ckpt-20250824-132747 at 2025-08-24T13:27:47.713626+00:00Z


---
**Latest checkpoint**: ckpt-20250824-134257 at 2025-08-24T13:42:57.611068+00:00Z


---
**Latest checkpoint**: ckpt-20250824-135817 at 2025-08-24T13:58:17.716868+00:00Z


---
**Latest checkpoint**: ckpt-20250824-141327 at 2025-08-24T14:13:27.742738+00:00Z


---
**Latest checkpoint**: ckpt-20250824-142835 at 2025-08-24T14:28:36.041210+00:00Z


---
**Latest checkpoint**: ckpt-20250824-144350 at 2025-08-24T14:43:50.975208+00:00Z


---
**Latest checkpoint**: ckpt-20250824-145857 at 2025-08-24T14:58:57.755083+00:00Z


---
**Latest checkpoint**: ckpt-20250824-151414 at 2025-08-24T15:14:15.006454+00:00Z


---
**Latest checkpoint**: ckpt-20250824-152922 at 2025-08-24T15:29:22.904097+00:00Z


---
**Latest checkpoint**: ckpt-20250824-154427 at 2025-08-24T15:44:27.749848+00:00Z


---
**Latest checkpoint**: ckpt-20250824-155928 at 2025-08-24T15:59:28.651054+00:00Z


---
**Latest checkpoint**: ckpt-20250824-161428 at 2025-08-24T16:14:28.810943+00:00Z


---
**Latest checkpoint**: ckpt-20250824-162928 at 2025-08-24T16:29:28.804651+00:00Z


---
**Latest checkpoint**: ckpt-20250824-164447 at 2025-08-24T16:44:47.273129+00:00Z


---
**Latest checkpoint**: ckpt-20250824-165951 at 2025-08-24T16:59:51.266821+00:00Z


---
**Latest checkpoint**: ckpt-20250824-171451 at 2025-08-24T17:14:51.750520+00:00Z


---
**Latest checkpoint**: ckpt-20250824-172958 at 2025-08-24T17:29:58.861860+00:00Z


---
**Latest checkpoint**: ckpt-20250824-174510 at 2025-08-24T17:45:10.888005+00:00Z


---
**Latest checkpoint**: ckpt-20250824-180011 at 2025-08-24T18:00:11.216924+00:00Z


---
**Latest checkpoint**: ckpt-20250824-181527 at 2025-08-24T18:15:27.745033+00:00Z


---
**Latest checkpoint**: ckpt-20250824-183047 at 2025-08-24T18:30:47.699408+00:00Z


---
**Latest checkpoint**: ckpt-20250824-184547 at 2025-08-24T18:45:47.727482+00:00Z


---
**Latest checkpoint**: ckpt-20250824-190057 at 2025-08-24T19:00:57.763251+00:00Z


---
**Latest checkpoint**: ckpt-20250824-191600 at 2025-08-24T19:16:00.343724+00:00Z


---
**Latest checkpoint**: ckpt-20250824-193117 at 2025-08-24T19:31:17.728716+00:00Z


---
**Latest checkpoint**: ckpt-20250824-194625 at 2025-08-24T19:46:25.496163+00:00Z


---
**Latest checkpoint**: ckpt-20250824-200127 at 2025-08-24T20:01:27.772170+00:00Z


---
**Latest checkpoint**: ckpt-20250824-201647 at 2025-08-24T20:16:47.840181+00:00Z


---
**Latest checkpoint**: ckpt-20250824-203222 at 2025-08-24T20:32:22.620017+00:00Z


---
**Latest checkpoint**: ckpt-20250824-204727 at 2025-08-24T20:47:27.744740+00:00Z


---
**Latest checkpoint**: ckpt-20250824-210230 at 2025-08-24T21:02:30.242074+00:00Z


---
**Latest checkpoint**: ckpt-20250824-211757 at 2025-08-24T21:17:57.791750+00:00Z


---
**Latest checkpoint**: ckpt-20250824-213307 at 2025-08-24T21:33:07.718861+00:00Z


---
**Latest checkpoint**: ckpt-20250824-214827 at 2025-08-24T21:48:27.720433+00:00Z


---
**Latest checkpoint**: ckpt-20250824-220330 at 2025-08-24T22:03:30.286873+00:00Z


---
**Latest checkpoint**: ckpt-20250824-221836 at 2025-08-24T22:18:36.848262+00:00Z


---
**Latest checkpoint**: ckpt-20250824-223357 at 2025-08-24T22:33:57.718953+00:00Z


---
**Latest checkpoint**: ckpt-20250824-224927 at 2025-08-24T22:49:27.719195+00:00Z


---
**Latest checkpoint**: ckpt-20250824-230437 at 2025-08-24T23:04:37.713796+00:00Z


---
**Latest checkpoint**: ckpt-20250824-231952 at 2025-08-24T23:19:52.978368+00:00Z


---
**Latest checkpoint**: ckpt-20250824-233517 at 2025-08-24T23:35:17.740130+00:00Z


---
**Latest checkpoint**: ckpt-20250824-235019 at 2025-08-24T23:50:19.490999+00:00Z


---
**Latest checkpoint**: ckpt-20250825-000527 at 2025-08-25T00:05:27.722007+00:00Z


---
**Latest checkpoint**: ckpt-20250825-002029 at 2025-08-25T00:20:29.419722+00:00Z


---
**Latest checkpoint**: ckpt-20250825-003607 at 2025-08-25T00:36:07.763739+00:00Z


---
**Latest checkpoint**: ckpt-20250825-005111 at 2025-08-25T00:51:11.575137+00:00Z


---
**Latest checkpoint**: ckpt-20250825-010615 at 2025-08-25T01:06:15.152258+00:00Z


---
**Latest checkpoint**: ckpt-20250825-012123 at 2025-08-25T01:21:23.864255+00:00Z


---
**Latest checkpoint**: ckpt-20250825-013627 at 2025-08-25T01:36:27.698052+00:00Z


---
**Latest checkpoint**: ckpt-20250825-015128 at 2025-08-25T01:51:28.958116+00:00Z


---
**Latest checkpoint**: ckpt-20250825-020641 at 2025-08-25T02:06:41.631075+00:00Z


---
**Latest checkpoint**: ckpt-20250825-022141 at 2025-08-25T02:21:41.932490+00:00Z


---
**Latest checkpoint**: ckpt-20250825-023658 at 2025-08-25T02:36:58.848962+00:00Z


---
**Latest checkpoint**: ckpt-20250825-025222 at 2025-08-25T02:52:22.613119+00:00Z


---
**Latest checkpoint**: ckpt-20250825-030727 at 2025-08-25T03:07:27.727637+00:00Z


---
**Latest checkpoint**: ckpt-20250825-032256 at 2025-08-25T03:22:56.784021+00:00Z


---
**Latest checkpoint**: ckpt-20250825-033813 at 2025-08-25T03:38:13.935264+00:00Z


---
**Latest checkpoint**: ckpt-20250825-035316 at 2025-08-25T03:53:17.023624+00:00Z


---
**Latest checkpoint**: ckpt-20250825-040817 at 2025-08-25T04:08:17.722438+00:00Z


---
**Latest checkpoint**: ckpt-20250825-042325 at 2025-08-25T04:23:25.480233+00:00Z


---
**Latest checkpoint**: ckpt-20250825-043827 at 2025-08-25T04:38:27.718043+00:00Z


---
**Latest checkpoint**: ckpt-20250825-045349 at 2025-08-25T04:53:49.653119+00:00Z


---
**Latest checkpoint**: ckpt-20250825-050927 at 2025-08-25T05:09:27.748862+00:00Z


---
**Latest checkpoint**: ckpt-20250825-052447 at 2025-08-25T05:24:47.697303+00:00Z


---
**Latest checkpoint**: ckpt-20250825-054000 at 2025-08-25T05:40:00.728065+00:00Z


---
**Latest checkpoint**: ckpt-20250825-055501 at 2025-08-25T05:55:01.127223+00:00Z


---
**Latest checkpoint**: ckpt-20250825-061001 at 2025-08-25T06:10:01.698052+00:00Z


---
**Latest checkpoint**: ckpt-20250825-062517 at 2025-08-25T06:25:17.737389+00:00Z


---
**Latest checkpoint**: ckpt-20250825-064017 at 2025-08-25T06:40:17.744129+00:00Z


---
**Latest checkpoint**: ckpt-20250825-065527 at 2025-08-25T06:55:27.700974+00:00Z


---
**Latest checkpoint**: ckpt-20250825-071037 at 2025-08-25T07:10:37.739292+00:00Z


---
**Latest checkpoint**: ckpt-20250825-072607 at 2025-08-25T07:26:07.715367+00:00Z


---
**Latest checkpoint**: ckpt-20250825-074117 at 2025-08-25T07:41:17.709936+00:00Z


---
**Latest checkpoint**: ckpt-20250825-075619 at 2025-08-25T07:56:19.365814+00:00Z


---
**Latest checkpoint**: ckpt-20250825-081127 at 2025-08-25T08:11:27.825184+00:00Z


---
**Latest checkpoint**: ckpt-20250825-082707 at 2025-08-25T08:27:07.733619+00:00Z


---
**Latest checkpoint**: ckpt-20250825-084227 at 2025-08-25T08:42:27.708753+00:00Z


---
**Latest checkpoint**: ckpt-20250825-085747 at 2025-08-25T08:57:47.733847+00:00Z


---
**Latest checkpoint**: ckpt-20250825-091257 at 2025-08-25T09:12:57.711359+00:00Z


---
**Latest checkpoint**: ckpt-20250825-092807 at 2025-08-25T09:28:07.770334+00:00Z


---
**Latest checkpoint**: ckpt-20250825-094327 at 2025-08-25T09:43:27.714767+00:00Z


---
**Latest checkpoint**: ckpt-20250825-095857 at 2025-08-25T09:58:57.729473+00:00Z


---
**Latest checkpoint**: ckpt-20250825-101427 at 2025-08-25T10:14:27.712439+00:00Z


---
**Latest checkpoint**: ckpt-20250825-102937 at 2025-08-25T10:29:37.723856+00:00Z


---
**Latest checkpoint**: ckpt-20250825-104438 at 2025-08-25T10:44:38.645407+00:00Z


---
**Latest checkpoint**: ckpt-20250825-110017 at 2025-08-25T11:00:17.756241+00:00Z


---
**Latest checkpoint**: ckpt-20250825-111518 at 2025-08-25T11:15:18.917240+00:00Z


---
**Latest checkpoint**: ckpt-20250825-113027 at 2025-08-25T11:30:27.742921+00:00Z


---
**Latest checkpoint**: ckpt-20250825-114554 at 2025-08-25T11:45:54.306494+00:00Z
