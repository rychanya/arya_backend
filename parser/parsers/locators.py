STAT_TOTAL: str = (
    '//div[@title="Правильно отвеченных вопросов в тесте"]/div[@class="wtq-stat-value"]'
)
STAT_UNANSWERED: str = (
    '//div[@title="Еще не отвеченных вопросов в тесте"]/div[@class="wtq-stat-value"]'
)

STAT_ANSWERED: str = (
    '//div[@title="Уже отвеченных вопросов в тесте"]/div[@class="wtq-stat-value"]'
)

STAT_PASSED: str = (
    '//div[@title="Правильно отвеченных вопросов в тесте"]/div[@class="wtq-stat-value"]'
)

STAT_FAILED: str = '//div[@title="Неправильно отвеченных вопросов в тесте"]/div[@class="wtq-stat-value"]'

Q_SUBMIT_BTN = '//button[contains(@class, "wtq-btn-submit") and not(contains(@class, "wtq-btn-disabled"))]/div[text()="Ответить и перейти далее"]'

FINAL = '//div[@class="wtq-body"]/div[@class="wtq-final"]'

JOIN_LEFT = '//table[@class="wtq-match-table"]//td[@class="wtq-match-left"]//div[@class="wtq-item-text-cell-main"]'
JOIN_RIGHT = '//table[@class="wtq-match-table"]//td[@class="wtq-match-right"]//div[@class="wtq-item-text-cell-main"]'
