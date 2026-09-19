package com.fakenews.server.domain.post.dto;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

@Data
public class PostRegisterReqDto {
    @NotBlank(message = "본문을 입력해 주세요.")
    @Size(max = 10000, message = "본문은 10,000자 이하로 입력해 주세요.")
    private String content;
}
