@callbacks_router.callback_query(ChooseLessonCallbackData.filter())
@logger.catch
async def attendance_send_callback(
    callback: CallbackQuery,
    callback_data: ChooseLessonCallbackData,
    student: StudentDTO,
    lesson_service: LessonService,
    attendance_service: AttendanceService,
):
    if callback.message is None:
        return

    logger.trace("attendance callback handled")

    lessons = await lesson_service.filter_by_group_id(student.group_id)
    choosen_lesson = next(filter(lambda lesson: lesson.id == callback_data.lesson_id, lessons))

    group_attendance = await attendance_service.get_visit_status_for_group_students(student.group_id, choosen_lesson.id)
    attendance_list_msg = attendance_for_headmen_message(group_attendance)

    await callback.message.edit_text(
        text=f"{choosen_lesson}\n\n{attendance_list_msg}",
        reply_markup=choose_lesson_buttons(lessons),
    )
