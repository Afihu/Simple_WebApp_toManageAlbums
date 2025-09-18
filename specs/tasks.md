# Tasks: Web App to Manage Albums

**Input**: Design documents from `/specs/`
**Prerequisites**: plan.md (required), data-model.md, API_contracts.md

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

---

## Phase 3.1: Setup
- [X] T001 Create backend and frontend project structure per implementation plan
- [X] T002 Initialize Python backend with AWS Lambda, boto3, pytest dependencies in `backend/`
- [X] T003 Initialize frontend with React/JS boilerplate in `frontend/`
- [ ] T004 [P] Configure linting and formatting tools for backend (`backend/`) and frontend (`frontend/`)

## Phase 3.2: Tests First (TDD)
- [X] T005 [P] Contract test GET /albums in `backend/tests/contract/test_albums_get.py`
- [X] T006 [P] Contract test POST /albums in `backend/tests/contract/test_albums_post.py`
- [X] T007 [P] Contract test GET /albums/{album_id} in `backend/tests/contract/test_albums_get_id.py`
- [X] T008 [P] Contract test PUT /albums/{album_id} in `backend/tests/contract/test_albums_put_id.py`
- [X] T009 [P] Contract test DELETE /albums/{album_id} in `backend/tests/contract/test_albums_delete_id.py`
- [X] T010 [P] Contract test GET /albums/{album_id}/images in `backend/tests/contract/test_images_get.py`
- [X] T011 [P] Contract test POST /albums/{album_id}/images in `backend/tests/contract/test_images_post.py`
- [X] T012 [P] Contract test GET /albums/{album_id}/images/{image_id} in `backend/tests/contract/test_images_get_id.py`
- [X] T013 [P] Contract test PUT /albums/{album_id}/images/{image_id} in `backend/tests/contract/test_images_put_id.py`
- [X] T014 [P] Contract test DELETE /albums/{album_id}/images/{image_id} in `backend/tests/contract/test_images_delete_id.py`
- [X] T015 [P] Contract test GET /quota in `backend/tests/contract/test_quota_get.py`
- [ ] T016 [P] Integration test: user registration and authentication in `backend/tests/integration/test_auth.py`
- [ ] T017 [P] Integration test: album CRUD flow in `backend/tests/integration/test_album_crud.py`
- [ ] T018 [P] Integration test: image upload and quota enforcement in `backend/tests/integration/test_image_upload.py`

## Phase 3.3: Core Implementation
- [ ] T019 [P] User model in `backend/src/models/user.py`
- [ ] T020 [P] Album model in `backend/src/models/album.py`
- [ ] T021 [P] Image model in `backend/src/models/image.py`
- [ ] T022 [P] Quota model in `backend/src/models/quota.py`
- [ ] T023 [P] AlbumService CRUD in `backend/src/services/album_service.py`
- [ ] T024 [P] ImageService CRUD in `backend/src/services/image_service.py`
- [ ] T025 [P] QuotaService in `backend/src/services/quota_service.py`
- [ ] T026 Implement GET /albums endpoint in `backend/src/api/albums.py`
- [ ] T027 Implement POST /albums endpoint in `backend/src/api/albums.py`
- [ ] T028 Implement GET /albums/{album_id} endpoint in `backend/src/api/albums.py`
- [ ] T029 Implement PUT /albums/{album_id} endpoint in `backend/src/api/albums.py`
- [ ] T030 Implement DELETE /albums/{album_id} endpoint in `backend/src/api/albums.py`
- [ ] T031 Implement GET /albums/{album_id}/images endpoint in `backend/src/api/images.py`
- [ ] T032 Implement POST /albums/{album_id}/images endpoint in `backend/src/api/images.py`
- [ ] T033 Implement GET /albums/{album_id}/images/{image_id} endpoint in `backend/src/api/images.py`
- [ ] T034 Implement PUT /albums/{album_id}/images/{image_id} endpoint in `backend/src/api/images.py`
- [ ] T035 Implement DELETE /albums/{album_id}/images/{image_id} endpoint in `backend/src/api/images.py`
- [ ] T036 Implement GET /quota endpoint in `backend/src/api/quota.py`

## Phase 3.4: Integration
- [ ] T037 Connect AlbumService and ImageService to DynamoDB in `backend/src/services/`
- [ ] T038 Integrate S3 for image storage in `backend/src/services/image_service.py`
- [ ] T039 Implement Cognito authentication middleware in `backend/src/api/`
- [ ] T040 Implement error handling and logging to CloudWatch in `backend/src/services/`
- [ ] T041 Implement CORS and security headers in API Gateway config

## Phase 3.5: Polish
- [ ] T042 [P] Unit tests for models in `backend/tests/unit/test_models.py`
- [ ] T043 [P] Unit tests for services in `backend/tests/unit/test_services.py`
- [ ] T044 [P] Unit tests for API endpoints in `backend/tests/unit/test_api.py`
- [ ] T045 [P] Performance tests (<200ms p95) in `backend/tests/perf/test_performance.py`
- [ ] T046 [P] Update API docs in `specs/API_contracts.md`
- [ ] T047 [P] Update README and quickstart in `specs/`
- [ ] T048 [P] Manual smoke test and validation

## Dependencies
- Setup (T001-T004) before all
- Tests (T005-T018) before implementation (T019-T041)
- Models (T019-T022) before services (T023-T025)
- Services before endpoints (T026-T036)
- Core before integration (T037-T041)
- Implementation before polish (T042-T048)

## Parallel Example
```
# Launch T005-T018 together:
Contract and integration tests for all endpoints and flows
# Launch T019-T022 together:
Model creation for User, Album, Image, Quota
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Avoid: vague tasks, same file conflicts
