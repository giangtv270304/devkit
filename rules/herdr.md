# Mở agent khi đang chạy trong Herdr

Khi session chạy trong Herdr (`echo $HC_TERMINAL_ID` ra một địa chỉ) và người dùng bảo mở, tạo hoặc giao việc cho "agent khác", "một agent", "agent riêng", "agent mới", thì mở agent đó thành pane Herdr cạnh mình:

```sh
python3 ~/.claude/skills/herdr-dispatch/dispatch.py <thư mục làm việc> <tên ngắn> "<việc, kèm giới hạn: chỉ đọc hay được ghi>" --template helper
```

Không dùng Agent tool cho yêu cầu này. Lý do: người dùng muốn thấy agent chạy cạnh mình và nói chuyện thẳng với nó; subagent chạy nền thì họ không thấy và không chen vào được.

- Agent tool vẫn dùng cho việc đọc hay tìm kiếm nội bộ mà người dùng không yêu cầu agent riêng, và cho subagent của `/work` khi không giao qua `herdr-dispatch`.
- Bước ghi code của một task đã có kế hoạch thì dùng `--template worker` theo skill `herdr-dispatch`.
- Sau khi mở, nói một dòng: tên pane, terminal, việc đã giao. Chờ báo về bằng `hc wait --children any` chạy nền, không dùng `sleep`.
- Ngoài Herdr (biến trống, ví dụ Claude desktop) thì dùng Agent tool như thường.
