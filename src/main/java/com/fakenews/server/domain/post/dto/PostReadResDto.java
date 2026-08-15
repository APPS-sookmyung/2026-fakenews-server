package com.fakenews.server.domain.post.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class PostReadResDto {
    private Long postId;

    private Long simulationId;

    private Long participantId;

    private Long originalPostId;

    private String content;

    private Boolean isInitial;

    private LocalDateTime createdAt;

    private LocalDateTime updatedAt;

    private Boolean deleted;

    private Long userId;

    private Long simulationAgentId;
}
