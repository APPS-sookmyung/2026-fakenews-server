package com.fakenews.server.domain.like.entity;

import com.fakenews.server.domain.post.entity.Post;
import com.fakenews.server.domain.participant.entity.Participant; // Participant 위치에 맞춰 수정
import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;

import java.time.LocalDateTime;

@Entity
@Table(name = "post_like")
@Getter
@NoArgsConstructor
public class PostLike {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "like_id")
    private Long likeId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "post_id")
    private Post post;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "participant_id")
    private Participant participant;

    @CreatedDate
    @Column(name = "created_at")
    private LocalDateTime createdAt;
}