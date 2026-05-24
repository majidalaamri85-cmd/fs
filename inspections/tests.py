from django.test import RequestFactory, TestCase

from .models import Evaluation, Item, Response, ResponseImage, Section
from .views import build_evaluation_insights, save_evaluation_from_request


class EvaluationImageSaveTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.section = Section.objects.create(title="Section", order=1)
        self.item = Item.objects.create(section=self.section, number=1, text="Item")
        self.evaluation = Evaluation.objects.create(
            facility_name="Facility",
            visit_date="2026-05-24",
        )
        self.response = Response.objects.create(
            evaluation=self.evaluation,
            item=self.item,
            status="non_compliant",
        )
        self.image = ResponseImage.objects.create(
            response=self.response,
            image="evaluation_images/existing.jpg",
        )

    def post_request(self, extra_post=None):
        data = {
            "facility_name": "Facility updated",
            "visit_date": "2026-05-24",
            f"status_{self.item.id}": "non_compliant",
            f"notes_{self.item.id}": "Updated notes",
            f"corrective_{self.item.id}": "Updated corrective action",
            f"duration_{self.item.id}": "7 days",
        }
        if extra_post:
            data.update(extra_post)
        return self.factory.post("/report/1/edit/", data=data)

    def test_existing_images_remain_when_editing_without_new_uploads(self):
        save_evaluation_from_request(self.post_request(), self.evaluation)

        self.response.refresh_from_db()
        self.assertEqual(list(self.response.images.values_list("id", flat=True)), [self.image.id])

    def test_existing_images_are_deleted_only_when_marked_for_deletion(self):
        save_evaluation_from_request(
            self.post_request({"deleted_images": [str(self.image.id)]}),
            self.evaluation,
        )

        self.assertFalse(ResponseImage.objects.filter(id=self.image.id).exists())

    def test_blank_status_does_not_delete_response_with_existing_images(self):
        save_evaluation_from_request(
            self.post_request({f"status_{self.item.id}": ""}),
            self.evaluation,
        )

        self.assertTrue(Response.objects.filter(id=self.response.id).exists())
        self.assertTrue(ResponseImage.objects.filter(id=self.image.id).exists())

    def test_smart_insights_flag_missing_corrective_data(self):
        self.item.priority = "عالية"
        self.item.save()
        self.evaluation.score = 80
        self.evaluation.save()
        self.response.corrective_action = ""
        self.response.correction_duration = ""
        self.response.save()
        self.image.delete()

        insights = build_evaluation_insights(
            self.evaluation,
            Response.objects.filter(evaluation=self.evaluation).select_related("item", "item__section").prefetch_related("images"),
            [],
        )

        self.assertEqual(insights["risk_level"], "مرتفع")
        self.assertEqual(insights["high_priority_count"], 1)
        self.assertEqual(insights["missing_photos_count"], 1)
        self.assertEqual(insights["missing_corrective_count"], 1)

    def test_report_detail_renders_smart_analysis(self):
        response = self.client.get(f"/report/{self.evaluation.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تحليل ذكي للتقرير")

    def test_statistics_dashboard_renders_smart_analysis(self):
        response = self.client.get("/statistics/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تحليل ذكي عام")
