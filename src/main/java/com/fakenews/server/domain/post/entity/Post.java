package com.fakenews.server.domain.post.entity;

import jakarta.persistence.*;
import lombok.Getter;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Getter
@Entity
public class Post {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long postId;

    private Long simulationId;

    private Long participantId;
    
    private Long originalPostId;

    private String content;

    private Boolean isInitial;

    @CreationTimestamp
    @Column(name = "created_at",updatable = false)
    private LocalDateTime createdAt;

    @CreationTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    @Column(name = "deleted", insertable = false)
    private Boolean deleted;

    private Long userId;

    private Long simulationAgentId;
}
