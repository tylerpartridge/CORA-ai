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


---
**Latest checkpoint**: ckpt-20250825-115415 at 2025-08-25T11:54:15.398068+00:00Z


---
**Latest checkpoint**: ckpt-20250825-120127 at 2025-08-25T12:01:27.986359+00:00Z


---
**Latest checkpoint**: ckpt-20250825-121647 at 2025-08-25T12:16:47.729994+00:00Z


---
**Latest checkpoint**: ckpt-20250825-121950 at 2025-08-25T12:19:50.104805+00:00Z


---
**Latest checkpoint**: ckpt-20250825-122412 at 2025-08-25T12:24:12.815338+00:00Z


---
**Latest checkpoint**: ckpt-20250825-122433 at 2025-08-25T12:24:33.283906+00:00Z


---
**Latest checkpoint**: ckpt-20250825-122512 at 2025-08-25T12:25:12.832488+00:00Z


---
**Latest checkpoint**: ckpt-20250825-122731 at 2025-08-25T12:27:31.140371+00:00Z


---
**Latest checkpoint**: ckpt-20250825-124013 at 2025-08-25T12:40:13.196038+00:00Z


---
**Latest checkpoint**: ckpt-20250825-125535 at 2025-08-25T12:55:35.683697+00:00Z


---
**Latest checkpoint**: ckpt-20250825-131045 at 2025-08-25T13:10:45.693899+00:00Z


---
**Latest checkpoint**: ckpt-20250825-132459 at 2025-08-25T13:24:59.748977+00:00Z


---
**Latest checkpoint**: ckpt-20250825-132547 at 2025-08-25T13:25:47.740967+00:00Z


---
**Latest checkpoint**: ckpt-20250825-134056 at 2025-08-25T13:40:56.306489+00:00Z


---
**Latest checkpoint**: ckpt-20250825-134147 at 2025-08-25T13:41:47.802589+00:00Z


---
**Latest checkpoint**: ckpt-20250825-135532 at 2025-08-25T13:55:32.453345+00:00Z


---
**Latest checkpoint**: ckpt-20250825-135625 at 2025-08-25T13:56:25.442529+00:00Z


---
**Latest checkpoint**: ckpt-20250825-135740 at 2025-08-25T13:57:40.037502+00:00Z


---
**Latest checkpoint**: ckpt-20250825-141145 at 2025-08-25T14:11:45.465468+00:00Z


---
**Latest checkpoint**: ckpt-20250825-142655 at 2025-08-25T14:26:55.436398+00:00Z


---
**Latest checkpoint**: ckpt-20250825-144230 at 2025-08-25T14:42:30.969207+00:00Z


---
**Latest checkpoint**: ckpt-20250825-145745 at 2025-08-25T14:57:45.481044+00:00Z


---
**Latest checkpoint**: ckpt-20250825-151249 at 2025-08-25T15:12:49.556053+00:00Z


---
**Latest checkpoint**: ckpt-20250825-152755 at 2025-08-25T15:27:55.441826+00:00Z


---
**Latest checkpoint**: ckpt-20250825-154329 at 2025-08-25T15:43:29.295554+00:00Z


---
**Latest checkpoint**: ckpt-20250825-155838 at 2025-08-25T15:58:38.163340+00:00Z


---
**Latest checkpoint**: ckpt-20250825-161355 at 2025-08-25T16:13:55.416085+00:00Z


---
**Latest checkpoint**: ckpt-20250825-162945 at 2025-08-25T16:29:45.423491+00:00Z


---
**Latest checkpoint**: ckpt-20250825-164449 at 2025-08-25T16:44:49.149728+00:00Z


---
**Latest checkpoint**: ckpt-20250825-165955 at 2025-08-25T16:59:55.464576+00:00Z


---
**Latest checkpoint**: ckpt-20250825-171501 at 2025-08-25T17:15:01.403499+00:00Z


---
**Latest checkpoint**: ckpt-20250825-173022 at 2025-08-25T17:30:22.160398+00:00Z


---
**Latest checkpoint**: ckpt-20250825-174542 at 2025-08-25T17:45:42.251564+00:00Z


---
**Latest checkpoint**: ckpt-20250825-180055 at 2025-08-25T18:00:55.476018+00:00Z


---
**Latest checkpoint**: ckpt-20250825-181611 at 2025-08-25T18:16:11.136418+00:00Z


---
**Latest checkpoint**: ckpt-20250825-183155 at 2025-08-25T18:31:55.452227+00:00Z


---
**Latest checkpoint**: ckpt-20250825-184725 at 2025-08-25T18:47:25.437771+00:00Z


---
**Latest checkpoint**: ckpt-20250825-190235 at 2025-08-25T19:02:35.449828+00:00Z


---
**Latest checkpoint**: ckpt-20250825-191745 at 2025-08-25T19:17:45.475890+00:00Z


---
**Latest checkpoint**: ckpt-20250825-193255 at 2025-08-25T19:32:55.426926+00:00Z


---
**Latest checkpoint**: ckpt-20250825-194428 at 2025-08-25T19:44:28.193729+00:00Z


---
**Latest checkpoint**: ckpt-20250825-195940 at 2025-08-25T19:59:40.950486+00:00Z


---
**Latest checkpoint**: ckpt-20250825-201446 at 2025-08-25T20:14:46.716692+00:00Z


---
**Latest checkpoint**: ckpt-20250825-202955 at 2025-08-25T20:29:55.439810+00:00Z


---
**Latest checkpoint**: ckpt-20250825-204501 at 2025-08-25T20:45:01.137926+00:00Z


---
**Latest checkpoint**: ckpt-20250825-210025 at 2025-08-25T21:00:25.514255+00:00Z


---
**Latest checkpoint**: ckpt-20250825-211535 at 2025-08-25T21:15:35.445799+00:00Z


---
**Latest checkpoint**: ckpt-20250825-213049 at 2025-08-25T21:30:49.338247+00:00Z


---
**Latest checkpoint**: ckpt-20250825-214549 at 2025-08-25T21:45:49.795005+00:00Z


---
**Latest checkpoint**: ckpt-20250825-220055 at 2025-08-25T22:00:55.445673+00:00Z


---
**Latest checkpoint**: ckpt-20250825-221636 at 2025-08-25T22:16:36.530022+00:00Z


---
**Latest checkpoint**: ckpt-20250825-223149 at 2025-08-25T22:31:49.773180+00:00Z


---
**Latest checkpoint**: ckpt-20250825-224655 at 2025-08-25T22:46:55.434325+00:00Z


---
**Latest checkpoint**: ckpt-20250825-230235 at 2025-08-25T23:02:35.459942+00:00Z


---
**Latest checkpoint**: ckpt-20250825-231745 at 2025-08-25T23:17:45.424222+00:00Z


---
**Latest checkpoint**: ckpt-20250825-233255 at 2025-08-25T23:32:55.432415+00:00Z


---
**Latest checkpoint**: ckpt-20250825-234829 at 2025-08-25T23:48:29.850810+00:00Z


---
**Latest checkpoint**: ckpt-20250826-000348 at 2025-08-26T00:03:48.230371+00:00Z


---
**Latest checkpoint**: ckpt-20250826-001855 at 2025-08-26T00:18:55.432389+00:00Z


---
**Latest checkpoint**: ckpt-20250826-003435 at 2025-08-26T00:34:35.475755+00:00Z


---
**Latest checkpoint**: ckpt-20250826-004945 at 2025-08-26T00:49:45.418694+00:00Z


---
**Latest checkpoint**: ckpt-20250826-010455 at 2025-08-26T01:04:55.484577+00:00Z


---
**Latest checkpoint**: ckpt-20250826-012005 at 2025-08-26T01:20:05.629894+00:00Z


---
**Latest checkpoint**: ckpt-20250826-013523 at 2025-08-26T01:35:23.419928+00:00Z


---
**Latest checkpoint**: ckpt-20250826-015040 at 2025-08-26T01:50:40.087408+00:00Z


---
**Latest checkpoint**: ckpt-20250826-020555 at 2025-08-26T02:05:55.417738+00:00Z


---
**Latest checkpoint**: ckpt-20250826-022145 at 2025-08-26T02:21:45.427114+00:00Z


---
**Latest checkpoint**: ckpt-20250826-023652 at 2025-08-26T02:36:52.321253+00:00Z


---
**Latest checkpoint**: ckpt-20250826-025155 at 2025-08-26T02:51:55.424189+00:00Z


---
**Latest checkpoint**: ckpt-20250826-030725 at 2025-08-26T03:07:25.424684+00:00Z


---
**Latest checkpoint**: ckpt-20250826-032255 at 2025-08-26T03:22:55.423417+00:00Z


---
**Latest checkpoint**: ckpt-20250826-033805 at 2025-08-26T03:38:05.429225+00:00Z


---
**Latest checkpoint**: ckpt-20250826-035319 at 2025-08-26T03:53:19.501635+00:00Z


---
**Latest checkpoint**: ckpt-20250826-040843 at 2025-08-26T04:08:43.603641+00:00Z


---
**Latest checkpoint**: ckpt-20250826-042345 at 2025-08-26T04:23:45.425782+00:00Z


---
**Latest checkpoint**: ckpt-20250826-043846 at 2025-08-26T04:38:46.715841+00:00Z


---
**Latest checkpoint**: ckpt-20250826-045355 at 2025-08-26T04:53:55.427637+00:00Z


---
**Latest checkpoint**: ckpt-20250826-050935 at 2025-08-26T05:09:35.101437+00:00Z


---
**Latest checkpoint**: ckpt-20250826-052455 at 2025-08-26T05:24:55.461573+00:00Z


---
**Latest checkpoint**: ckpt-20250826-054035 at 2025-08-26T05:40:35.446718+00:00Z


---
**Latest checkpoint**: ckpt-20250826-055545 at 2025-08-26T05:55:45.473702+00:00Z


---
**Latest checkpoint**: ckpt-20250826-061055 at 2025-08-26T06:10:55.430850+00:00Z


---
**Latest checkpoint**: ckpt-20250826-062557 at 2025-08-26T06:25:57.184452+00:00Z


---
**Latest checkpoint**: ckpt-20250826-064057 at 2025-08-26T06:40:57.376698+00:00Z


---
**Latest checkpoint**: ckpt-20250826-065609 at 2025-08-26T06:56:09.985216+00:00Z


---
**Latest checkpoint**: ckpt-20250826-071125 at 2025-08-26T07:11:25.433693+00:00Z


---
**Latest checkpoint**: ckpt-20250826-072635 at 2025-08-26T07:26:35.419104+00:00Z


---
**Latest checkpoint**: ckpt-20250826-074136 at 2025-08-26T07:41:36.414781+00:00Z


---
**Latest checkpoint**: ckpt-20250826-075645 at 2025-08-26T07:56:45.419547+00:00Z


---
**Latest checkpoint**: ckpt-20250826-081155 at 2025-08-26T08:11:55.431383+00:00Z


---
**Latest checkpoint**: ckpt-20250826-082704 at 2025-08-26T08:27:04.778318+00:00Z


---
**Latest checkpoint**: ckpt-20250826-084255 at 2025-08-26T08:42:55.436841+00:00Z


---
**Latest checkpoint**: ckpt-20250826-085825 at 2025-08-26T08:58:25.440380+00:00Z


---
**Latest checkpoint**: ckpt-20250826-091335 at 2025-08-26T09:13:35.425775+00:00Z


---
**Latest checkpoint**: ckpt-20250826-092855 at 2025-08-26T09:28:55.420557+00:00Z


---
**Latest checkpoint**: ckpt-20250826-094356 at 2025-08-26T09:43:56.254791+00:00Z


---
**Latest checkpoint**: ckpt-20250826-095909 at 2025-08-26T09:59:09.605399+00:00Z


---
**Latest checkpoint**: ckpt-20250826-101445 at 2025-08-26T10:14:45.428437+00:00Z


---
**Latest checkpoint**: ckpt-20250826-102955 at 2025-08-26T10:29:55.418865+00:00Z


---
**Latest checkpoint**: ckpt-20250826-104503 at 2025-08-26T10:45:03.928125+00:00Z


---
**Latest checkpoint**: ckpt-20250826-110018 at 2025-08-26T11:00:18.416393+00:00Z


---
**Latest checkpoint**: ckpt-20250826-111520 at 2025-08-26T11:15:20.250298+00:00Z


---
**Latest checkpoint**: ckpt-20250826-113040 at 2025-08-26T11:30:40.933088+00:00Z


---
**Latest checkpoint**: ckpt-20250826-114541 at 2025-08-26T11:45:41.548570+00:00Z


---
**Latest checkpoint**: ckpt-20250826-120055 at 2025-08-26T12:00:55.477872+00:00Z


---
**Latest checkpoint**: ckpt-20250826-121615 at 2025-08-26T12:16:15.455076+00:00Z


---
**Latest checkpoint**: ckpt-20250826-123125 at 2025-08-26T12:31:25.705071+00:00Z


---
**Latest checkpoint**: ckpt-20250826-124633 at 2025-08-26T12:46:33.150970+00:00Z


---
**Latest checkpoint**: ckpt-20250826-130138 at 2025-08-26T13:01:38.259450+00:00Z


---
**Latest checkpoint**: ckpt-20250826-131639 at 2025-08-26T13:16:39.199482+00:00Z


---
**Latest checkpoint**: ckpt-20250826-133155 at 2025-08-26T13:31:55.436329+00:00Z


---
**Latest checkpoint**: ckpt-20250826-134729 at 2025-08-26T13:47:29.990820+00:00Z


---
**Latest checkpoint**: ckpt-20250826-140231 at 2025-08-26T14:02:31.725072+00:00Z


---
**Latest checkpoint**: ckpt-20250826-141745 at 2025-08-26T14:17:45.798557+00:00Z


---
**Latest checkpoint**: ckpt-20250826-143255 at 2025-08-26T14:32:55.432220+00:00Z


---
**Latest checkpoint**: ckpt-20250826-144804 at 2025-08-26T14:48:05.016750+00:00Z


---
**Latest checkpoint**: ckpt-20250826-150305 at 2025-08-26T15:03:05.271466+00:00Z


---
**Latest checkpoint**: ckpt-20250826-151806 at 2025-08-26T15:18:06.510580+00:00Z


---
**Latest checkpoint**: ckpt-20250826-153312 at 2025-08-26T15:33:13.022130+00:00Z


---
**Latest checkpoint**: ckpt-20250826-154814 at 2025-08-26T15:48:14.290029+00:00Z


---
**Latest checkpoint**: ckpt-20250826-160315 at 2025-08-26T16:03:15.442427+00:00Z


---
**Latest checkpoint**: ckpt-20250826-161825 at 2025-08-26T16:18:25.488915+00:00Z


---
**Latest checkpoint**: ckpt-20250826-163326 at 2025-08-26T16:33:26.341186+00:00Z


---
**Latest checkpoint**: ckpt-20250826-164855 at 2025-08-26T16:48:55.486056+00:00Z


---
**Latest checkpoint**: ckpt-20250826-170435 at 2025-08-26T17:04:35.433611+00:00Z


---
**Latest checkpoint**: ckpt-20250826-171945 at 2025-08-26T17:19:45.432844+00:00Z


---
**Latest checkpoint**: ckpt-20250826-173455 at 2025-08-26T17:34:55.436499+00:00Z


---
**Latest checkpoint**: ckpt-20250826-175020 at 2025-08-26T17:50:20.038206+00:00Z


---
**Latest checkpoint**: ckpt-20250826-180535 at 2025-08-26T18:05:35.425730+00:00Z


---
**Latest checkpoint**: ckpt-20250826-182044 at 2025-08-26T18:20:44.112723+00:00Z


---
**Latest checkpoint**: ckpt-20250826-183555 at 2025-08-26T18:35:55.443671+00:00Z


---
**Latest checkpoint**: ckpt-20250826-185058 at 2025-08-26T18:50:58.545835+00:00Z


---
**Latest checkpoint**: ckpt-20250826-190635 at 2025-08-26T19:06:35.745275+00:00Z


---
**Latest checkpoint**: ckpt-20250826-192146 at 2025-08-26T19:21:46.786410+00:00Z
