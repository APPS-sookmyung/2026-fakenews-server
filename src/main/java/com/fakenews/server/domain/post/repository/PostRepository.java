package com.fakenews.server.domain.post.repository;

import com.fakenews.server.domain.post.entity.Post;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PostRepository extends JpaRepository<Post, Long> {
}
