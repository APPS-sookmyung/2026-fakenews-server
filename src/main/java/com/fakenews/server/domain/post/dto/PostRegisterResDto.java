package com.fakenews.server.domain.post.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class PostRegisterResDto {
    private Long postId;
}
